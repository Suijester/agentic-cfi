; ModuleID = 'targets/example1/example1.c'
source_filename = "targets/example1/example1.c"
target datalayout = "e-m:o-i64:64-i128:128-n32:64-S128"
target triple = "arm64-apple-macosx14.0.0"

@.str = private unnamed_addr constant [28 x i8] c"SAFE: safe_handler reached.\00", align 1, !dbg !0
@.str.1 = private unnamed_addr constant [30 x i8] c"ADMIN: admin_handler reached.\00", align 1, !dbg !7
@.str.2 = private unnamed_addr constant [29 x i8] c"UNSAFE: debug_shell reached.\00", align 1, !dbg !12
@.str.3 = private unnamed_addr constant [5 x i8] c"safe\00", align 1, !dbg !17
@handler = internal global ptr null, align 8, !dbg !22
@.str.4 = private unnamed_addr constant [6 x i8] c"admin\00", align 1, !dbg !28
@.str.5 = private unnamed_addr constant [36 x i8] c"SIMULATED HIJACK: overwrote handler\00", align 1, !dbg !33
@.str.6 = private unnamed_addr constant [21 x i8] c"ERR: handler is NULL\00", align 1, !dbg !38
@.str.7 = private unnamed_addr constant [7 x i8] c"attack\00", align 1, !dbg !43
@.str.8 = private unnamed_addr constant [35 x i8] c"Usage: %s [safe | attack | admin]\0A\00", align 1, !dbg !48

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @safe_handler() #0 !dbg !65 {
  %1 = call i32 @puts(ptr noundef @.str), !dbg !67
  ret void, !dbg !68
}

declare i32 @puts(ptr noundef) #1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @admin_handler() #0 !dbg !69 {
  %1 = call i32 @puts(ptr noundef @.str.1), !dbg !70
  ret void, !dbg !71
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @debug_shell() #0 !dbg !72 {
  %1 = call i32 @puts(ptr noundef @.str.2), !dbg !73
  ret void, !dbg !74
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @set_handler_from_mode(ptr noundef %0) #0 !dbg !75 {
  %2 = alloca ptr, align 8
  store ptr %0, ptr %2, align 8
  call void @llvm.dbg.declare(metadata ptr %2, metadata !80, metadata !DIExpression()), !dbg !81
  %3 = load ptr, ptr %2, align 8, !dbg !82
  %4 = call i32 @strcmp(ptr noundef %3, ptr noundef @.str.3), !dbg !84
  %5 = icmp eq i32 %4, 0, !dbg !85
  br i1 %5, label %6, label %7, !dbg !86

6:                                                ; preds = %1
  store ptr @safe_handler, ptr @handler, align 8, !dbg !87
  br label %14, !dbg !89

7:                                                ; preds = %1
  %8 = load ptr, ptr %2, align 8, !dbg !90
  %9 = call i32 @strcmp(ptr noundef %8, ptr noundef @.str.4), !dbg !92
  %10 = icmp eq i32 %9, 0, !dbg !93
  br i1 %10, label %11, label %12, !dbg !94

11:                                               ; preds = %7
  store ptr @admin_handler, ptr @handler, align 8, !dbg !95
  br label %13, !dbg !97

12:                                               ; preds = %7
  store ptr @safe_handler, ptr @handler, align 8, !dbg !98
  br label %13

13:                                               ; preds = %12, %11
  br label %14

14:                                               ; preds = %13, %6
  ret void, !dbg !100
}

; Function Attrs: nocallback nofree nosync nounwind readnone speculatable willreturn
declare void @llvm.dbg.declare(metadata, metadata, metadata) #2

declare i32 @strcmp(ptr noundef, ptr noundef) #1

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @sim_hijack() #0 !dbg !101 {
  %1 = call i32 @puts(ptr noundef @.str.5), !dbg !102
  store ptr @debug_shell, ptr @handler, align 8, !dbg !103
  ret void, !dbg !104
}

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define void @dispatch() #0 !dbg !105 {
  %1 = load ptr, ptr @handler, align 8, !dbg !106
  %2 = icmp eq ptr %1, null, !dbg !108
  br i1 %2, label %3, label %5, !dbg !109

3:                                                ; preds = %0
  %4 = call i32 @puts(ptr noundef @.str.6), !dbg !110
  call void @exit(i32 noundef 1) #4, !dbg !112
  unreachable, !dbg !112

5:                                                ; preds = %0
  %6 = load ptr, ptr @handler, align 8, !dbg !113
  call void %6(), !dbg !113
  ret void, !dbg !114
}

; Function Attrs: noreturn
declare void @exit(i32 noundef) #3

; Function Attrs: noinline nounwind optnone ssp uwtable(sync)
define i32 @main(i32 noundef %0, ptr noundef %1) #0 !dbg !115 {
  %3 = alloca i32, align 4
  %4 = alloca i32, align 4
  %5 = alloca ptr, align 8
  %6 = alloca ptr, align 8
  store i32 0, ptr %3, align 4
  store i32 %0, ptr %4, align 4
  call void @llvm.dbg.declare(metadata ptr %4, metadata !121, metadata !DIExpression()), !dbg !122
  store ptr %1, ptr %5, align 8
  call void @llvm.dbg.declare(metadata ptr %5, metadata !123, metadata !DIExpression()), !dbg !124
  call void @llvm.dbg.declare(metadata ptr %6, metadata !125, metadata !DIExpression()), !dbg !126
  %7 = load i32, ptr %4, align 4, !dbg !127
  %8 = icmp sgt i32 %7, 1, !dbg !128
  br i1 %8, label %9, label %13, !dbg !129

9:                                                ; preds = %2
  %10 = load ptr, ptr %5, align 8, !dbg !130
  %11 = getelementptr inbounds ptr, ptr %10, i64 1, !dbg !130
  %12 = load ptr, ptr %11, align 8, !dbg !130
  br label %14, !dbg !129

13:                                               ; preds = %2
  br label %14, !dbg !129

14:                                               ; preds = %13, %9
  %15 = phi ptr [ %12, %9 ], [ @.str.3, %13 ], !dbg !129
  store ptr %15, ptr %6, align 8, !dbg !126
  %16 = load ptr, ptr %6, align 8, !dbg !131
  %17 = call i32 @strcmp(ptr noundef %16, ptr noundef @.str.3), !dbg !133
  %18 = icmp eq i32 %17, 0, !dbg !134
  br i1 %18, label %23, label %19, !dbg !135

19:                                               ; preds = %14
  %20 = load ptr, ptr %6, align 8, !dbg !136
  %21 = call i32 @strcmp(ptr noundef %20, ptr noundef @.str.4), !dbg !137
  %22 = icmp eq i32 %21, 0, !dbg !138
  br i1 %22, label %23, label %25, !dbg !139

23:                                               ; preds = %19, %14
  %24 = load ptr, ptr %6, align 8, !dbg !140
  call void @set_handler_from_mode(ptr noundef %24), !dbg !142
  br label %36, !dbg !143

25:                                               ; preds = %19
  %26 = load ptr, ptr %6, align 8, !dbg !144
  %27 = call i32 @strcmp(ptr noundef %26, ptr noundef @.str.7), !dbg !146
  %28 = icmp eq i32 %27, 0, !dbg !147
  br i1 %28, label %29, label %30, !dbg !148

29:                                               ; preds = %25
  call void @set_handler_from_mode(ptr noundef @.str.3), !dbg !149
  call void @sim_hijack(), !dbg !151
  br label %35, !dbg !152

30:                                               ; preds = %25
  %31 = load ptr, ptr %5, align 8, !dbg !153
  %32 = getelementptr inbounds ptr, ptr %31, i64 0, !dbg !153
  %33 = load ptr, ptr %32, align 8, !dbg !153
  %34 = call i32 (ptr, ...) @printf(ptr noundef @.str.8, ptr noundef %33), !dbg !155
  call void @exit(i32 noundef 1) #4, !dbg !156
  unreachable, !dbg !156

35:                                               ; preds = %29
  br label %36

36:                                               ; preds = %35, %23
  call void @dispatch(), !dbg !157
  ret i32 0, !dbg !158
}

declare i32 @printf(ptr noundef, ...) #1

attributes #0 = { noinline nounwind optnone ssp uwtable(sync) "frame-pointer"="non-leaf" "min-legal-vector-width"="0" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #1 = { "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #2 = { nocallback nofree nosync nounwind readnone speculatable willreturn }
attributes #3 = { noreturn "frame-pointer"="non-leaf" "no-trapping-math"="true" "probe-stack"="__chkstk_darwin" "stack-protector-buffer-size"="8" "target-cpu"="apple-m1" "target-features"="+aes,+crc,+crypto,+dotprod,+fp-armv8,+fp16fml,+fullfp16,+lse,+neon,+ras,+rcpc,+rdm,+sha2,+sha3,+sm4,+v8.1a,+v8.2a,+v8.3a,+v8.4a,+v8.5a,+v8a,+zcm,+zcz" }
attributes #4 = { noreturn }

!llvm.module.flags = !{!57, !58, !59, !60, !61, !62, !63}
!llvm.dbg.cu = !{!24}
!llvm.ident = !{!64}

!0 = !DIGlobalVariableExpression(var: !1, expr: !DIExpression())
!1 = distinct !DIGlobalVariable(scope: null, file: !2, line: 8, type: !3, isLocal: true, isDefinition: true)
!2 = !DIFile(filename: "targets/example1/example1.c", directory: "/Users/akisub/agentic-cfi")
!3 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 224, elements: !5)
!4 = !DIBasicType(name: "char", size: 8, encoding: DW_ATE_signed_char)
!5 = !{!6}
!6 = !DISubrange(count: 28)
!7 = !DIGlobalVariableExpression(var: !8, expr: !DIExpression())
!8 = distinct !DIGlobalVariable(scope: null, file: !2, line: 12, type: !9, isLocal: true, isDefinition: true)
!9 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 240, elements: !10)
!10 = !{!11}
!11 = !DISubrange(count: 30)
!12 = !DIGlobalVariableExpression(var: !13, expr: !DIExpression())
!13 = distinct !DIGlobalVariable(scope: null, file: !2, line: 16, type: !14, isLocal: true, isDefinition: true)
!14 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 232, elements: !15)
!15 = !{!16}
!16 = !DISubrange(count: 29)
!17 = !DIGlobalVariableExpression(var: !18, expr: !DIExpression())
!18 = distinct !DIGlobalVariable(scope: null, file: !2, line: 22, type: !19, isLocal: true, isDefinition: true)
!19 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 40, elements: !20)
!20 = !{!21}
!21 = !DISubrange(count: 5)
!22 = !DIGlobalVariableExpression(var: !23, expr: !DIExpression())
!23 = distinct !DIGlobalVariable(name: "handler", scope: !24, file: !2, line: 19, type: !53, isLocal: true, isDefinition: true)
!24 = distinct !DICompileUnit(language: DW_LANG_C99, file: !2, producer: "Apple clang version 15.0.0 (clang-1500.3.9.4)", isOptimized: false, runtimeVersion: 0, emissionKind: FullDebug, retainedTypes: !25, globals: !27, splitDebugInlining: false, nameTableKind: None, sysroot: "/Applications/Xcode.app/Contents/Developer/Platforms/MacOSX.platform/Developer/SDKs/MacOSX.sdk", sdk: "MacOSX.sdk")
!25 = !{!26}
!26 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: null, size: 64)
!27 = !{!0, !7, !12, !17, !28, !33, !38, !43, !48, !22}
!28 = !DIGlobalVariableExpression(var: !29, expr: !DIExpression())
!29 = distinct !DIGlobalVariable(scope: null, file: !2, line: 24, type: !30, isLocal: true, isDefinition: true)
!30 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 48, elements: !31)
!31 = !{!32}
!32 = !DISubrange(count: 6)
!33 = !DIGlobalVariableExpression(var: !34, expr: !DIExpression())
!34 = distinct !DIGlobalVariable(scope: null, file: !2, line: 33, type: !35, isLocal: true, isDefinition: true)
!35 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 288, elements: !36)
!36 = !{!37}
!37 = !DISubrange(count: 36)
!38 = !DIGlobalVariableExpression(var: !39, expr: !DIExpression())
!39 = distinct !DIGlobalVariable(scope: null, file: !2, line: 39, type: !40, isLocal: true, isDefinition: true)
!40 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 168, elements: !41)
!41 = !{!42}
!42 = !DISubrange(count: 21)
!43 = !DIGlobalVariableExpression(var: !44, expr: !DIExpression())
!44 = distinct !DIGlobalVariable(scope: null, file: !2, line: 51, type: !45, isLocal: true, isDefinition: true)
!45 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 56, elements: !46)
!46 = !{!47}
!47 = !DISubrange(count: 7)
!48 = !DIGlobalVariableExpression(var: !49, expr: !DIExpression())
!49 = distinct !DIGlobalVariable(scope: null, file: !2, line: 55, type: !50, isLocal: true, isDefinition: true)
!50 = !DICompositeType(tag: DW_TAG_array_type, baseType: !4, size: 280, elements: !51)
!51 = !{!52}
!52 = !DISubrange(count: 35)
!53 = !DIDerivedType(tag: DW_TAG_typedef, name: "handler_t", file: !2, line: 5, baseType: !54)
!54 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !55, size: 64)
!55 = !DISubroutineType(types: !56)
!56 = !{null}
!57 = !{i32 2, !"SDK Version", [2 x i32] [i32 14, i32 5]}
!58 = !{i32 7, !"Dwarf Version", i32 4}
!59 = !{i32 2, !"Debug Info Version", i32 3}
!60 = !{i32 1, !"wchar_size", i32 4}
!61 = !{i32 8, !"PIC Level", i32 2}
!62 = !{i32 7, !"uwtable", i32 1}
!63 = !{i32 7, !"frame-pointer", i32 1}
!64 = !{!"Apple clang version 15.0.0 (clang-1500.3.9.4)"}
!65 = distinct !DISubprogram(name: "safe_handler", scope: !2, file: !2, line: 7, type: !55, scopeLine: 7, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!66 = !{}
!67 = !DILocation(line: 8, column: 5, scope: !65)
!68 = !DILocation(line: 9, column: 1, scope: !65)
!69 = distinct !DISubprogram(name: "admin_handler", scope: !2, file: !2, line: 11, type: !55, scopeLine: 11, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!70 = !DILocation(line: 12, column: 5, scope: !69)
!71 = !DILocation(line: 13, column: 1, scope: !69)
!72 = distinct !DISubprogram(name: "debug_shell", scope: !2, file: !2, line: 15, type: !55, scopeLine: 15, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!73 = !DILocation(line: 16, column: 5, scope: !72)
!74 = !DILocation(line: 17, column: 1, scope: !72)
!75 = distinct !DISubprogram(name: "set_handler_from_mode", scope: !2, file: !2, line: 21, type: !76, scopeLine: 21, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!76 = !DISubroutineType(types: !77)
!77 = !{null, !78}
!78 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !79, size: 64)
!79 = !DIDerivedType(tag: DW_TAG_const_type, baseType: !4)
!80 = !DILocalVariable(name: "mode", arg: 1, scope: !75, file: !2, line: 21, type: !78)
!81 = !DILocation(line: 21, column: 40, scope: !75)
!82 = !DILocation(line: 22, column: 16, scope: !83)
!83 = distinct !DILexicalBlock(scope: !75, file: !2, line: 22, column: 9)
!84 = !DILocation(line: 22, column: 9, scope: !83)
!85 = !DILocation(line: 22, column: 30, scope: !83)
!86 = !DILocation(line: 22, column: 9, scope: !75)
!87 = !DILocation(line: 23, column: 17, scope: !88)
!88 = distinct !DILexicalBlock(scope: !83, file: !2, line: 22, column: 36)
!89 = !DILocation(line: 24, column: 5, scope: !88)
!90 = !DILocation(line: 24, column: 23, scope: !91)
!91 = distinct !DILexicalBlock(scope: !83, file: !2, line: 24, column: 16)
!92 = !DILocation(line: 24, column: 16, scope: !91)
!93 = !DILocation(line: 24, column: 38, scope: !91)
!94 = !DILocation(line: 24, column: 16, scope: !83)
!95 = !DILocation(line: 25, column: 17, scope: !96)
!96 = distinct !DILexicalBlock(scope: !91, file: !2, line: 24, column: 44)
!97 = !DILocation(line: 26, column: 5, scope: !96)
!98 = !DILocation(line: 27, column: 17, scope: !99)
!99 = distinct !DILexicalBlock(scope: !91, file: !2, line: 26, column: 12)
!100 = !DILocation(line: 29, column: 1, scope: !75)
!101 = distinct !DISubprogram(name: "sim_hijack", scope: !2, file: !2, line: 32, type: !55, scopeLine: 32, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!102 = !DILocation(line: 33, column: 5, scope: !101)
!103 = !DILocation(line: 34, column: 13, scope: !101)
!104 = !DILocation(line: 35, column: 1, scope: !101)
!105 = distinct !DISubprogram(name: "dispatch", scope: !2, file: !2, line: 37, type: !55, scopeLine: 37, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!106 = !DILocation(line: 38, column: 9, scope: !107)
!107 = distinct !DILexicalBlock(scope: !105, file: !2, line: 38, column: 9)
!108 = !DILocation(line: 38, column: 17, scope: !107)
!109 = !DILocation(line: 38, column: 9, scope: !105)
!110 = !DILocation(line: 39, column: 9, scope: !111)
!111 = distinct !DILexicalBlock(scope: !107, file: !2, line: 38, column: 26)
!112 = !DILocation(line: 40, column: 9, scope: !111)
!113 = !DILocation(line: 43, column: 5, scope: !105)
!114 = !DILocation(line: 44, column: 1, scope: !105)
!115 = distinct !DISubprogram(name: "main", scope: !2, file: !2, line: 46, type: !116, scopeLine: 46, flags: DIFlagPrototyped, spFlags: DISPFlagDefinition, unit: !24, retainedNodes: !66)
!116 = !DISubroutineType(types: !117)
!117 = !{!118, !118, !119}
!118 = !DIBasicType(name: "int", size: 32, encoding: DW_ATE_signed)
!119 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !120, size: 64)
!120 = !DIDerivedType(tag: DW_TAG_pointer_type, baseType: !4, size: 64)
!121 = !DILocalVariable(name: "argc", arg: 1, scope: !115, file: !2, line: 46, type: !118)
!122 = !DILocation(line: 46, column: 14, scope: !115)
!123 = !DILocalVariable(name: "argv", arg: 2, scope: !115, file: !2, line: 46, type: !119)
!124 = !DILocation(line: 46, column: 27, scope: !115)
!125 = !DILocalVariable(name: "mode", scope: !115, file: !2, line: 47, type: !78)
!126 = !DILocation(line: 47, column: 17, scope: !115)
!127 = !DILocation(line: 47, column: 25, scope: !115)
!128 = !DILocation(line: 47, column: 30, scope: !115)
!129 = !DILocation(line: 47, column: 24, scope: !115)
!130 = !DILocation(line: 47, column: 37, scope: !115)
!131 = !DILocation(line: 49, column: 16, scope: !132)
!132 = distinct !DILexicalBlock(scope: !115, file: !2, line: 49, column: 9)
!133 = !DILocation(line: 49, column: 9, scope: !132)
!134 = !DILocation(line: 49, column: 30, scope: !132)
!135 = !DILocation(line: 49, column: 35, scope: !132)
!136 = !DILocation(line: 49, column: 45, scope: !132)
!137 = !DILocation(line: 49, column: 38, scope: !132)
!138 = !DILocation(line: 49, column: 60, scope: !132)
!139 = !DILocation(line: 49, column: 9, scope: !115)
!140 = !DILocation(line: 50, column: 31, scope: !141)
!141 = distinct !DILexicalBlock(scope: !132, file: !2, line: 49, column: 66)
!142 = !DILocation(line: 50, column: 9, scope: !141)
!143 = !DILocation(line: 51, column: 5, scope: !141)
!144 = !DILocation(line: 51, column: 23, scope: !145)
!145 = distinct !DILexicalBlock(scope: !132, file: !2, line: 51, column: 16)
!146 = !DILocation(line: 51, column: 16, scope: !145)
!147 = !DILocation(line: 51, column: 39, scope: !145)
!148 = !DILocation(line: 51, column: 16, scope: !132)
!149 = !DILocation(line: 52, column: 9, scope: !150)
!150 = distinct !DILexicalBlock(scope: !145, file: !2, line: 51, column: 45)
!151 = !DILocation(line: 53, column: 9, scope: !150)
!152 = !DILocation(line: 54, column: 5, scope: !150)
!153 = !DILocation(line: 55, column: 55, scope: !154)
!154 = distinct !DILexicalBlock(scope: !145, file: !2, line: 54, column: 12)
!155 = !DILocation(line: 55, column: 9, scope: !154)
!156 = !DILocation(line: 56, column: 9, scope: !154)
!157 = !DILocation(line: 59, column: 5, scope: !115)
!158 = !DILocation(line: 60, column: 5, scope: !115)
