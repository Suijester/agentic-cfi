#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/IRBuilder.h"
#include "llvm/Plugins/PassPlugin.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/JSON.h"
#include "llvm/Support/MemoryBuffer.h"
#include "llvm/Support/raw_ostream.h"

using namespace llvm;

static cl::opt<std::string> policyFile(
    "cfi-policy",
    cl::desc("Path to CFI JSON file"),
    cl::value_desc("filename")
);

// policy parsing (read CFI files and parse JSON)

struct cfi_rule {
    std::string caller;
    int call_index;
    std::vector<std::string> allowed_targets;
};

static std::vector<cfi_rule> parsePolicy(StringRef path) {
    std::vector<cfi_rule> rules;
    
    auto buffer = MemoryBuffer::getFile(path);
    if (!buffer) {
        errs() << "LLVM Pass: can't open policy file: " << path << "\n";
        return rules;
    }

    auto json_parsed = json::parse((*buffer)->getBuffer());
    if (!json_parsed) {
        errs() << "LLVM Pass: failed to evaluate policy file JSON";
        return rules;
    }

    auto* arr = json_parsed->getAsArray();
    if (!arr) {
        errs() << "LLVM Pass: failed to convert JSON to array";
        return rules;
    }

    for (auto& elem: *arr) {
        auto* obj = elem.getAsObject();
        if (!obj) continue;

        cfi_rule rule;
        if (auto caller = obj->getString("caller")) {
            rule.caller = caller->str();
        }

        if (auto index = obj->getInteger("call_index")) {
            rule.call_index = *index;
        } else {
            rule.call_index = -1;
        }

        if (auto* targets = obj -> getArray("allowed_targets")) {
            for (auto& targ: *targets) {
                if (auto str = targ.getAsString()) {
                    rule.allowed_targets.push_back(str->str());
                }
            }
        }
        rules.push_back(rule);
    }
    return rules;
}

// LLVM pass after parsing JSON

namespace {
struct cfi_enforce_pass : public PassInfoMixin<cfi_enforce_pass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &MAM) {
        if (policyFile.empty()) {
            errs() << "LLVM Pass: no policy file given :(";
            return PreservedAnalyses::all();
        }

        auto rules = parsePolicy(policyFile);
        if (rules.empty()) {
            errs() << "LLVM Pass: no rules able to be parsed";
            return PreservedAnalyses::all();
        }

        bool modified = false;
        for (auto& F : M) {
            if (F.isDeclaration()) continue;

            int callIndex = 0;
            std::vector<CallBase*> indirectCalls;

            for (auto& BB: F) {
                for (auto& I : BB) {
                    if (auto* CB = dyn_cast<CallBase>(&I)) {
                        if (CB->isIndirectCall()) {
                            indirectCalls.push_back(CB);
                        }
                    }
                }
            }

            for (auto* CB : indirectCalls) {
                const cfi_rule* matchedRule = nullptr;
                for (const auto &rule: rules) {
                    if (rule.caller == F.getName().str() && rule.call_index == callIndex) {
                        matchedRule = &rule;
                        break;
                    }
                }
                callIndex++;

                if (!matchedRule || matchedRule->allowed_targets.empty()) {
                    continue;
                }

                // insert the CFI check before indirect call
                IRBuilder<> Builder(CB);
                Value* callee = CB->getCalledOperand();

                Value* isValid = ConstantInt::getFalse(M.getContext());
                for (const auto& targetName : matchedRule->allowed_targets) {
                    Function* target = M.getFunction(targetName);
                    if (!target) {
                        errs() << "LLVM Pass: targeted function by CFI '" << targetName << "' not found in module";
                        continue;
                    }
                    Value* targetPtr = Builder.CreatePointerCast(target, callee->getType());
                    Value* cmp = Builder.CreateICmpEQ(callee, targetPtr);
                    isValid = Builder.CreateOr(isValid, cmp);
                }

                Instruction* splitPoint = CB;
                BasicBlock* originalBB = splitPoint->getParent();
                BasicBlock* continueBB = originalBB->splitBasicBlock(splitPoint, "cfi.continue");
                BasicBlock* abortBB = BasicBlock::Create(M.getContext(), "cfi.abort", &F, continueBB);

                originalBB->getTerminator()->eraseFromParent();
                IRBuilder<> BrBuilder(originalBB);
                BrBuilder.CreateCondBr(isValid, continueBB, abortBB);

                IRBuilder<> AbortBuilder(abortBB);
                FunctionCallee AbortFn = M.getOrInsertFunction("abort", FunctionType::get(Type::getVoidTy(M.getContext()), false));
                AbortBuilder.CreateCall(AbortFn);
                AbortBuilder.CreateUnreachable();

                modified = true;
            }
        }

        return modified ? PreservedAnalyses::none() : PreservedAnalyses::all();
    }
};
}

// plugin registration to LLVM
extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo llvmGetPassPluginInfo() {
    return {
        LLVM_PLUGIN_API_VERSION, "CFIEnforce", LLVM_VERSION_STRING,
        [](PassBuilder &PB) {
            PB.registerPipelineParsingCallback(
                [](StringRef Name, ModulePassManager& MPM, 
                ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "cfi-enforce") {
                        MPM.addPass(cfi_enforce_pass());
                        return true;
                    }
                    return false;
                }
            );
        }
    };
}