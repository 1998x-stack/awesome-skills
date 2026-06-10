# Lua C API 完整参考

## 目录
1. [初始化与生命周期](#1-初始化与生命周期)
2. [栈操作完整 API](#2-栈操作完整-api)
3. [类型系统与检查](#3-类型系统与检查)
4. [表操作](#4-表操作)
5. [函数注册与调用](#5-函数注册与调用)
6. [Userdata 与 Metatable](#6-userdata-与-metatable)
7. [错误处理](#7-错误处理)
8. [协程 C API](#8-协程-c-api)
9. [注册表与引用](#9-注册表与引用)
10. [辅助库 luaL_*](#10-辅助库-lual_)

---

## 1. 初始化与生命周期

```c
#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"

// 创建新的 Lua 状态机（带默认内存分配器）
lua_State *L = luaL_newstate();

// 创建自定义内存分配器的状态机
void *allocator(void *ud, void *ptr, size_t osize, size_t nsize) {
    if (nsize == 0) { free(ptr); return NULL; }
    return realloc(ptr, nsize);
}
lua_State *L = lua_newstate(allocator, NULL);

// 加载标准库
luaL_openlibs(L);           // 全部标准库
luaopen_base(L);            // 基础库（print, pcall 等）
luaopen_math(L);            // 数学库
luaopen_string(L);          // 字符串库
luaopen_table(L);           // 表库
luaopen_io(L);              // IO 库
luaopen_os(L);              // OS 库
luaopen_package(L);         // 包管理
luaopen_coroutine(L);       // 协程库
luaopen_debug(L);           // 调试库
luaopen_utf8(L);            // UTF8 库 (5.3+)

// 执行
luaL_dofile(L, "script.lua");              // 加载并执行文件
luaL_dostring(L, "return 1 + 1");         // 加载并执行字符串
luaL_loadfile(L, "script.lua");           // 仅加载（不执行）
luaL_loadstring(L, "return 1 + 1");      // 仅加载字符串
lua_load(L, reader, data, name, mode);    // 自定义 reader

// 关闭
lua_close(L);  // 销毁状态机，释放所有内存
```

---

## 2. 栈操作完整 API

### 压栈（Push）

```c
lua_pushnil(L);                     // nil
lua_pushboolean(L, int b);          // boolean
lua_pushnumber(L, lua_Number n);    // number (通常是 double)
lua_pushinteger(L, lua_Integer i);  // integer (Lua 5.3+)
lua_pushunsigned(L, lua_Unsigned u);// unsigned (仅 Lua 5.2)
lua_pushstring(L, const char *s);   // string（内部复制）
lua_pushlstring(L, const char *s, size_t len);  // 带长度字符串
lua_pushfstring(L, const char *fmt, ...);       // 格式化字符串（类 printf）
lua_pushvfstring(L, fmt, va_list);  // va_list 版本
lua_pushcfunction(L, lua_CFunction);// C 函数
lua_pushcclosure(L, fn, int n);     // C 闭包（n 个 upvalue）
lua_pushvalue(L, int idx);          // 复制栈上元素
lua_pushlightuserdata(L, void *p);  // 轻量 userdata
lua_pushthread(L);                  // 将当前线程压栈

// 全局表相关
lua_pushglobaltable(L);             // 将全局表压栈 (Lua 5.2+)
```

### 弹出与读取

```c
// 读取（不修改栈）
lua_toboolean(L, int idx)           // → int (0/1)
lua_tonumber(L, int idx)            // → lua_Number
lua_tonumberx(L, idx, int *isnum)   // 带成功标志 (5.3+)
lua_tointeger(L, int idx)           // → lua_Integer
lua_tointegerx(L, idx, int *isnum)  // 带成功标志
lua_tostring(L, int idx)            // → const char* (警告：可能修改栈！)
lua_tolstring(L, idx, size_t *len)  // → const char* + 长度
lua_tocfunction(L, int idx)         // → lua_CFunction
lua_touserdata(L, int idx)          // → void*
lua_tothread(L, int idx)            // → lua_State*
lua_topointer(L, int idx)           // → const void* (唯一标识符)

// 栈管理
int  lua_gettop(L)                  // 返回元素数量（= 栈顶索引）
void lua_settop(L, int n)           // 设置栈顶（n<当前则弹出，n>当前则补nil）
void lua_pop(L, int n)              // 弹出 n 个（= lua_settop(L, -n-1)）
void lua_remove(L, int idx)         // 移除位置 idx 的元素
void lua_insert(L, int idx)         // 将栈顶移入位置 idx
void lua_replace(L, int idx)        // 用栈顶替换位置 idx（弹出栈顶）
void lua_copy(L, int from, int to)  // 复制 from 到 to（5.2+）
void lua_rotate(L, int idx, int n)  // 旋转栈片段（5.3+）
int  lua_checkstack(L, int n)       // 确保有 n 个额外空间（失败返回0）
void lua_xmove(lua_State *from, lua_State *to, int n)  // 跨线程移动元素
```

### 栈索引速查

```
正索引: 1（栈底/最先压入）→ lua_gettop(L)（栈顶/最后压入）
负索引: -1（栈顶）→ -lua_gettop(L)（栈底）
伪索引: LUA_REGISTRYINDEX（注册表）
        LUA_ENVIRONINDEX（环境表，仅5.1）
        lua_upvalueindex(n)（第n个upvalue，1起始）
```

---

## 3. 类型系统与检查

```c
// 类型常量
LUA_TNONE       // -1（无效索引）
LUA_TNIL        // 0
LUA_TBOOLEAN    // 1
LUA_TLIGHTUSERDATA  // 2
LUA_TNUMBER     // 3
LUA_TSTRING     // 4
LUA_TTABLE      // 5
LUA_TFUNCTION   // 6
LUA_TUSERDATA   // 7
LUA_TTHREAD     // 8

// 类型查询
int lua_type(L, int idx)            // 返回类型常量
const char *lua_typename(L, int tp) // 类型名称字符串

// 类型测试（返回 0/1）
lua_isnil(L, idx)
lua_isnone(L, idx)                  // 无效索引
lua_isnoneornil(L, idx)
lua_isboolean(L, idx)
lua_isnumber(L, idx)                // 包括可转数字的字符串！
lua_isinteger(L, idx)               // (5.3+)
lua_isstring(L, idx)                // 包括数字（可转字符串）
lua_istable(L, idx)
lua_isfunction(L, idx)
lua_iscfunction(L, idx)
lua_isuserdata(L, idx)              // full or light
lua_islightuserdata(L, idx)
lua_isthread(L, idx)

// 相等性
lua_rawequal(L, idx1, idx2)         // 原始相等（不触发 __eq）
lua_compare(L, idx1, idx2, op)      // LUA_OPEQ/OPLT/OPLE (5.2+)
```

---

## 4. 表操作

```c
// 创建
lua_newtable(L)                         // {} 压栈
lua_createtable(L, int narr, int nrec)  // 预分配：narr 个数组位，nrec 个哈希位

// 读取字段（key → value 压栈）
lua_getfield(L, int tbl_idx, const char *key)   // table[key]
lua_rawget(L, int tbl_idx)                      // table[key]，不触发 __index
lua_rawgeti(L, int tbl_idx, lua_Integer n)      // table[n]，整数键，最快
lua_geti(L, int tbl_idx, lua_Integer n)         // table[n]（5.3+）
lua_gettable(L, int tbl_idx)                    // table[key]，key 在栈顶

// 设置字段（弹出 value）
lua_setfield(L, int tbl_idx, const char *key)   // table[key] = value
lua_rawset(L, int tbl_idx)                      // table[key] = value，不触发 __newindex
lua_rawseti(L, int tbl_idx, lua_Integer n)      // table[n] = value，整数键
lua_seti(L, int tbl_idx, lua_Integer n)         // table[n] = value（5.3+）
lua_settable(L, int tbl_idx)                    // table[key] = value

// 全局表
lua_getglobal(L, const char *name)  // 等价于 lua_getfield(L, LUA_GLOBALSINDEX, name)
lua_setglobal(L, const char *name)  // 等价于 lua_setfield(L, LUA_GLOBALSINDEX, name)

// 长度
lua_rawlen(L, int idx)   // # 操作符，无 __len
lua_len(L, int idx)      // # 操作符，触发 __len

// 迭代（注意：不是 pairs 的 C 等价，是更底层的）
lua_pushnil(L);
while (lua_next(L, tbl_idx) != 0) {
    // 栈: ... | key | value
    // 处理 key（idx = -2）和 value（idx = -1）
    lua_pop(L, 1);  // 弹出 value，保留 key 供下次迭代
}
```

---

## 5. 函数注册与调用

```c
// C 函数类型
typedef int (*lua_CFunction)(lua_State *L);
// 规则：从栈读参数（1 = 第一参），压栈返回值，返回返回值数量

// 注册单个函数
lua_pushcfunction(L, my_func);
lua_setglobal(L, "my_func");

// 批量注册（推荐方式）
static const luaL_Reg my_lib[] = {
    {"create",   my_create},
    {"destroy",  my_destroy},
    {"update",   my_update},
    {NULL, NULL}  // 哨兵
};
luaL_newlib(L, my_lib);      // 创建表并注册（5.2+）
lua_setglobal(L, "MyLib");

// C 闭包（带 upvalue 的 C 函数）
lua_pushinteger(L, counter_start);  // upvalue 1
lua_pushcfunction_upvalues:
lua_pushcclosure(L, my_closure, 1); // 1 个 upvalue
// 在 C 函数内通过 lua_upvalueindex(n) 访问 upvalue

// 调用 Lua 函数
// 方式1: lua_call（不安全，错误会 longjmp）
lua_getglobal(L, "my_func");
lua_pushnumber(L, 42.0);
lua_call(L, 1, 1);  // 1 参数, 1 返回值

// 方式2: lua_pcall（安全，推荐）
lua_getglobal(L, "my_func");
lua_pushnumber(L, 42.0);
int status = lua_pcall(L, 1, 1, 0);  // 最后参数: 错误处理函数在栈中的位置（0=无）
if (status != LUA_OK) {
    fprintf(stderr, "Error: %s\n", lua_tostring(L, -1));
    lua_pop(L, 1);
}

// 方式3: 带消息处理器的 pcall
lua_pushcfunction(L, error_handler);  // 先压入错误处理器
int handler_idx = lua_gettop(L);
lua_getglobal(L, "my_func");
lua_pushnumber(L, 42.0);
status = lua_pcall(L, 1, 1, handler_idx);
lua_remove(L, handler_idx);  // 清理处理器

// Lua 5.4 新增
lua_callk(L, nargs, nresults, ctx, k);   // 可让出版本
lua_pcallk(L, nargs, nresults, err, ctx, k);
```

---

## 6. Userdata 与 Metatable

```c
// Full Userdata（由 Lua GC 管理的 C 内存块）
void *lua_newuserdata(L, size_t size);          // 分配并压栈
void *lua_newuserdatauv(L, size_t size, int nuv); // 带 user values (5.4+)

// Light Userdata（只是 void* 指针，无 GC）
lua_pushlightuserdata(L, void *p);

// Metatable 操作
luaL_newmetatable(L, const char *name);         // 创建/获取命名 metatable
luaL_getmetatable(L, const char *name);         // 获取命名 metatable
lua_setmetatable(L, int idx);                   // 设置对象的 metatable
lua_getmetatable(L, int idx);                   // 获取对象的 metatable（返回0若无）

// 安全类型检查
void *luaL_checkudata(L, int idx, const char *tname); // 检查并返回 userdata
void *luaL_testudata(L, int idx, const char *tname);  // 不报错版本 (5.2+)

// 完整 OOP userdata 示例：
static void register_vec2(lua_State *L) {
    // 创建 metatable
    luaL_newmetatable(L, "Vec2");  // 栈: mt
    
    // __index = mt（让方法调用有效）
    lua_pushvalue(L, -1);          // 复制 mt
    lua_setfield(L, -2, "__index");// mt.__index = mt
    
    // __tostring
    lua_pushcfunction(L, vec2_tostring);
    lua_setfield(L, -2, "__tostring");
    
    // __add（运算符重载）
    lua_pushcfunction(L, vec2_add);
    lua_setfield(L, -2, "__add");
    
    // __gc（析构）
    lua_pushcfunction(L, vec2_gc);
    lua_setfield(L, -2, "__gc");
    
    // 方法
    static const luaL_Reg methods[] = {
        {"length",    vec2_length},
        {"normalize", vec2_normalize},
        {"dot",       vec2_dot},
        {NULL, NULL}
    };
    luaL_setfuncs(L, methods, 0);  // 注册方法到 mt
    
    lua_pop(L, 1);  // 弹出 metatable
}

// 创建 Vec2 的 C 函数
static int vec2_new(lua_State *L) {
    float x = (float)luaL_optnumber(L, 1, 0.0);
    float y = (float)luaL_optnumber(L, 2, 0.0);
    
    // 分配 userdata
    float *v = (float *)lua_newuserdata(L, 2 * sizeof(float));
    v[0] = x; v[1] = y;
    
    // 设置 metatable
    luaL_getmetatable(L, "Vec2");
    lua_setmetatable(L, -2);
    
    return 1;
}
```

---

## 7. 错误处理

```c
// 错误类型（lua_pcall 返回值）
LUA_OK        // 0: 成功
LUA_ERRRUN    // 2: 运行时错误
LUA_ERRMEM    // 4: 内存分配错误
LUA_ERRERR    // 5: 错误处理函数本身出错
LUA_ERRSYNTAX // 3: 语法错误（仅 luaL_loadstring 等）
LUA_ERRGCMM   // 6: GC 元方法错误 (5.2)
LUA_YIELD     // 1: 线程挂起（非错误）

// 抛出错误（从 C 函数内调用）
lua_error(L)                  // 抛出栈顶值作为错误
luaL_error(L, fmt, ...)       // 格式化错误消息并抛出
luaL_argerror(L, narg, msg)   // 参数错误（含位置信息）
luaL_typerror(L, narg, tname) // 类型错误

// 保护调用
lua_pcall(L, nargs, nresults, msgh)
lua_cpcall(L, func, ud)       // 保护调用 C 函数（仅5.1）

// traceback
luaL_traceback(L, L2, msg, level)  // 生成 traceback 字符串

// 典型错误处理器
static int traceback_handler(lua_State *L) {
    const char *msg = lua_tostring(L, 1);
    if (msg == NULL) {
        // 非字符串错误对象
        lua_pushliteral(L, "(non-string error)");
    } else {
        luaL_traceback(L, L, msg, 1);
    }
    return 1;
}
```

---

## 8. 协程 C API

```c
// 创建协程
lua_State *co = lua_newthread(L);  // 协程 = 轻量线程，共享 globals

// 启动/恢复协程
// Lua 5.4:
int nres;
int status = lua_resume(co, L, nargs, &nres);
// Lua 5.1/5.2/5.3:
int status = lua_resume(co, nargs);  // nres 通过 lua_gettop 获得

// 状态值
LUA_OK    // 协程正常结束
LUA_YIELD // 协程挂起（coroutine.yield）
LUA_ERRRUN // 运行时错误

// 检查协程状态
lua_status(co)     // 同上常量
lua_isyieldable(L) // 当前函数是否可以 yield

// 从 C 函数 yield（需要配合 lua_pcallk）
static int my_async_func(lua_State *L, int status, lua_KContext ctx) {
    if (status == LUA_YIELD) {
        // 从 yield 恢复后继续
    }
    return 0;
}
// 调用时：
lua_yieldk(L, nresults, ctx, my_async_func);  // 挂起并设置继续函数
```

---

## 9. 注册表与引用

```c
// 注册表：LUA_REGISTRYINDEX 处的特殊表，C 侧持久存储 Lua 值

// 方式1：整数键引用（推荐）
lua_pushvalue(L, -1);                           // 复制要存的值
int ref = luaL_ref(L, LUA_REGISTRYINDEX);       // 存入注册表，返回整数键
// 之后读取：
lua_rawgeti(L, LUA_REGISTRYINDEX, ref);         // 推入
// 释放：
luaL_unref(L, LUA_REGISTRYINDEX, ref);          // 删除引用

// 方式2：字符串键（用于固定已知名称）
lua_pushvalue(L, -1);
lua_setfield(L, LUA_REGISTRYINDEX, "my_key");
// 读取：
lua_getfield(L, LUA_REGISTRYINDEX, "my_key");

// 预定义注册表键
LUA_RIDX_MAINTHREAD  // 主线程（5.4+）
LUA_RIDX_GLOBALS     // 全局表（5.2+，替代 LUA_GLOBALSINDEX）

// 全局表访问（5.2+）
lua_rawgeti(L, LUA_REGISTRYINDEX, LUA_RIDX_GLOBALS);
```

---

## 10. 辅助库 luaL_*

```c
// 参数检查（类型错误时自动抛 Lua 错误，含位置信息）
luaL_checkboolean(L, narg)
luaL_checknumber(L, narg)     // → lua_Number
luaL_checkinteger(L, narg)    // → lua_Integer
luaL_checkstring(L, narg)     // → const char*
luaL_checklstring(L, narg, *l)// 带长度
luaL_checktype(L, narg, type) // 检查类型
luaL_checkany(L, narg)        // 检查任意非 nil

// 可选参数（有默认值）
luaL_optboolean(L, narg, def)
luaL_optnumber(L, narg, def)
luaL_optinteger(L, narg, def)
luaL_optstring(L, narg, def)

// 字符串缓冲区（高效字符串构建）
luaL_Buffer b;
luaL_buffinit(L, &b);
luaL_addstring(&b, "hello ");
luaL_addvalue(&b);             // 弹出栈顶字符串加入缓冲
char *p = luaL_prepbuffer(&b); // 获取写指针
memcpy(p, data, len);
luaL_addsize(&b, len);
luaL_pushresult(&b);           // 将结果字符串压栈

// 模块注册辅助
luaL_newlib(L, funcs)          // 创建新表并注册函数（5.2+）
luaL_newlibtable(L, funcs)     // 仅创建预分配大小的表
luaL_setfuncs(L, funcs, nup)   // 注册函数（支持 upvalue）

// 文件/字符串加载
luaL_loadfile(L, filename)
luaL_loadstring(L, str)
luaL_loadbuffer(L, buf, size, name)
luaL_dofile(L, filename)       // = loadfile + pcall
luaL_dostring(L, str)          // = loadstring + pcall

// 元表辅助
luaL_newmetatable(L, tname)    // 创建或获取具名 metatable
luaL_getmetatable(L, tname)    // 压入具名 metatable
luaL_setmetatable(L, tname)    // 设置栈顶对象的 metatable (5.3+)
luaL_checkudata(L, narg, tname)// 检查并返回 userdata
luaL_testudata(L, narg, tname) // 不报错版本

// 杂项
luaL_where(L, level)           // 压入位置字符串 "file:line: "
luaL_traceback(L, L2, msg, lvl)// 生成调用栈字符串
luaL_len(L, idx)               // lua_Integer 版的 # 操作
luaL_tolstring(L, idx, *len)   // 任意类型转字符串（调用 __tostring）
```
