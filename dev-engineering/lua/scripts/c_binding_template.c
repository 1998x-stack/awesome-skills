/*
 * c_binding_template.c — Lua C 绑定完整模板
 * 兼容: Lua 5.1 / 5.2 / 5.3 / 5.4 / LuaJIT
 *
 * 演示如何将 C 结构体和函数安全地暴露给 Lua，
 * 包括：全功能 OOP userdata、元表、GC 钩子、
 * 错误处理、跨版本兼容性宏。
 *
 * 编译示例（动态库，供 require 加载）:
 *   gcc -shared -fPIC -o mylib.so c_binding_template.c \
 *       $(pkg-config --cflags --libs lua5.4)
 *
 * Lua 使用:
 *   local lib = require("mylib")
 *   local v = lib.Vec2(3, 4)
 *   print(v:length())  -- 5.0
 *   print(v + lib.Vec2(1, 0))  -- Vec2(4, 4)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#include "lua.h"
#include "lualib.h"
#include "lauxlib.h"

/* ── 跨版本兼容宏 ─────────────────────────────────────── */

#if LUA_VERSION_NUM < 502
  /* Lua 5.1: 模拟 5.2+ API */
  #define luaL_newlib(L, l)  (lua_newtable(L), luaL_register(L, NULL, l))
  #define lua_rawlen(L, i)   lua_objlen(L, i)
  static void luaL_setfuncs(lua_State *L, const luaL_Reg *l, int nup) {
      for (; l->name; l++) {
          int i;
          for (i = 0; i < nup; i++) lua_pushvalue(L, -(nup));
          lua_pushcclosure(L, l->func, nup);
          lua_setfield(L, -(nup + 2), l->name);
      }
      lua_pop(L, nup);
  }
#endif

#if LUA_VERSION_NUM < 503
  /* Lua 5.1/5.2: 没有 lua_isinteger */
  #define lua_isinteger(L, i) 0
#endif

/* ── C 结构体定义 ─────────────────────────────────────── */

typedef struct {
    double x, y;
} Vec2;

typedef struct {
    Vec2 position;
    Vec2 velocity;
    double radius;
    int   active;
    char  tag[64];
} Entity;

/* ── Vec2 绑定 ─────────────────────────────────────────── */

#define VEC2_MT "Vec2"

/* 创建 Vec2 userdata 并推入栈 */
static Vec2 *push_vec2(lua_State *L, double x, double y) {
    Vec2 *v = (Vec2 *)lua_newuserdata(L, sizeof(Vec2));
    v->x = x;
    v->y = y;
    luaL_getmetatable(L, VEC2_MT);
    lua_setmetatable(L, -2);
    return v;
}

/* 获取并验证 Vec2 userdata */
static Vec2 *check_vec2(lua_State *L, int idx) {
    return (Vec2 *)luaL_checkudata(L, idx, VEC2_MT);
}

/* lib.Vec2(x, y) → Vec2 */
static int vec2_new(lua_State *L) {
    double x = luaL_optnumber(L, 1, 0.0);
    double y = luaL_optnumber(L, 2, 0.0);
    push_vec2(L, x, y);
    return 1;
}

/* v:length() → number */
static int vec2_length(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    lua_pushnumber(L, sqrt(v->x * v->x + v->y * v->y));
    return 1;
}

/* v:normalize() → Vec2 */
static int vec2_normalize(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    double len = sqrt(v->x * v->x + v->y * v->y);
    if (len < 1e-10) {
        luaL_error(L, "cannot normalize zero vector");
        return 0;
    }
    push_vec2(L, v->x / len, v->y / len);
    return 1;
}

/* v:dot(other) → number */
static int vec2_dot(lua_State *L) {
    Vec2 *a = check_vec2(L, 1);
    Vec2 *b = check_vec2(L, 2);
    lua_pushnumber(L, a->x * b->x + a->y * b->y);
    return 1;
}

/* v:lerp(other, t) → Vec2 */
static int vec2_lerp(lua_State *L) {
    Vec2 *a = check_vec2(L, 1);
    Vec2 *b = check_vec2(L, 2);
    double t = luaL_checknumber(L, 3);
    push_vec2(L, a->x + (b->x - a->x) * t, a->y + (b->y - a->y) * t);
    return 1;
}

/* v:clone() → Vec2 */
static int vec2_clone(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    push_vec2(L, v->x, v->y);
    return 1;
}

/* v:unpack() → x, y */
static int vec2_unpack(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    lua_pushnumber(L, v->x);
    lua_pushnumber(L, v->y);
    return 2;
}

/* __tostring */
static int vec2_tostring(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    lua_pushfstring(L, "Vec2(%g, %g)", v->x, v->y);
    return 1;
}

/* __add: v1 + v2 */
static int vec2_add(lua_State *L) {
    Vec2 *a = check_vec2(L, 1);
    Vec2 *b = check_vec2(L, 2);
    push_vec2(L, a->x + b->x, a->y + b->y);
    return 1;
}

/* __sub: v1 - v2 */
static int vec2_sub(lua_State *L) {
    Vec2 *a = check_vec2(L, 1);
    Vec2 *b = check_vec2(L, 2);
    push_vec2(L, a->x - b->x, a->y - b->y);
    return 1;
}

/* __mul: v * scalar 或 scalar * v */
static int vec2_mul(lua_State *L) {
    if (lua_isnumber(L, 1)) {
        double s = lua_tonumber(L, 1);
        Vec2 *v = check_vec2(L, 2);
        push_vec2(L, v->x * s, v->y * s);
    } else {
        Vec2 *v = check_vec2(L, 1);
        double s = luaL_checknumber(L, 2);
        push_vec2(L, v->x * s, v->y * s);
    }
    return 1;
}

/* __div: v / scalar */
static int vec2_div(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    double s = luaL_checknumber(L, 2);
    if (fabs(s) < 1e-10) luaL_error(L, "division by zero");
    push_vec2(L, v->x / s, v->y / s);
    return 1;
}

/* __unm: -v */
static int vec2_unm(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    push_vec2(L, -v->x, -v->y);
    return 1;
}

/* __eq: v1 == v2 */
static int vec2_eq(lua_State *L) {
    Vec2 *a = check_vec2(L, 1);
    Vec2 *b = check_vec2(L, 2);
    lua_pushboolean(L, (fabs(a->x - b->x) < 1e-10 && fabs(a->y - b->y) < 1e-10));
    return 1;
}

/* __index：允许 v.x / v.y 读取 */
static int vec2_index(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    const char *key = luaL_checkstring(L, 2);
    
    if (strcmp(key, "x") == 0) { lua_pushnumber(L, v->x); return 1; }
    if (strcmp(key, "y") == 0) { lua_pushnumber(L, v->y); return 1; }
    
    /* 查找方法表 */
    luaL_getmetatable(L, VEC2_MT);
    lua_pushvalue(L, 2);
    lua_rawget(L, -2);
    return 1;
}

/* __newindex：允许 v.x = 10 赋值 */
static int vec2_newindex(lua_State *L) {
    Vec2 *v = check_vec2(L, 1);
    const char *key = luaL_checkstring(L, 2);
    double val = luaL_checknumber(L, 3);
    
    if (strcmp(key, "x") == 0) { v->x = val; return 0; }
    if (strcmp(key, "y") == 0) { v->y = val; return 0; }
    
    luaL_error(L, "Vec2 has no field '%s'", key);
    return 0;
}

/* 方法表 */
static const luaL_Reg vec2_methods[] = {
    {"length",    vec2_length},
    {"normalize", vec2_normalize},
    {"dot",       vec2_dot},
    {"lerp",      vec2_lerp},
    {"clone",     vec2_clone},
    {"unpack",    vec2_unpack},
    {NULL, NULL}
};

/* 注册 Vec2 metatable */
static void register_vec2(lua_State *L) {
    luaL_newmetatable(L, VEC2_MT);          /* mt */
    
    lua_pushcfunction(L, vec2_index);
    lua_setfield(L, -2, "__index");
    
    lua_pushcfunction(L, vec2_newindex);
    lua_setfield(L, -2, "__newindex");
    
    lua_pushcfunction(L, vec2_tostring);
    lua_setfield(L, -2, "__tostring");
    
    lua_pushcfunction(L, vec2_add); lua_setfield(L, -2, "__add");
    lua_pushcfunction(L, vec2_sub); lua_setfield(L, -2, "__sub");
    lua_pushcfunction(L, vec2_mul); lua_setfield(L, -2, "__mul");
    lua_pushcfunction(L, vec2_div); lua_setfield(L, -2, "__div");
    lua_pushcfunction(L, vec2_unm); lua_setfield(L, -2, "__unm");
    lua_pushcfunction(L, vec2_eq);  lua_setfield(L, -2, "__eq");
    
    /* 注册方法到 mt（通过 __index 访问）*/
    luaL_setfuncs(L, vec2_methods, 0);
    
    lua_pop(L, 1);  /* 弹出 metatable */
}

/* ── Entity 绑定 ──────────────────────────────────────── */

#define ENTITY_MT "Entity"

static Entity *check_entity(lua_State *L, int idx) {
    return (Entity *)luaL_checkudata(L, idx, ENTITY_MT);
}

static int entity_new(lua_State *L) {
    double x     = luaL_optnumber(L, 1, 0.0);
    double y     = luaL_optnumber(L, 2, 0.0);
    double r     = luaL_optnumber(L, 3, 16.0);
    const char *tag = luaL_optstring(L, 4, "default");
    
    Entity *e = (Entity *)lua_newuserdata(L, sizeof(Entity));
    e->position.x = x;
    e->position.y = y;
    e->velocity.x = 0;
    e->velocity.y = 0;
    e->radius     = r;
    e->active     = 1;
    strncpy(e->tag, tag, 63);
    e->tag[63] = '\0';
    
    luaL_getmetatable(L, ENTITY_MT);
    lua_setmetatable(L, -2);
    return 1;
}

static int entity_update(lua_State *L) {
    Entity *e = check_entity(L, 1);
    double dt = luaL_checknumber(L, 2);
    e->position.x += e->velocity.x * dt;
    e->position.y += e->velocity.y * dt;
    return 0;
}

static int entity_get_pos(lua_State *L) {
    Entity *e = check_entity(L, 1);
    push_vec2(L, e->position.x, e->position.y);
    return 1;
}

static int entity_set_pos(lua_State *L) {
    Entity *e = check_entity(L, 1);
    Vec2 *v   = check_vec2(L, 2);
    e->position = *v;
    return 0;
}

static int entity_get_vel(lua_State *L) {
    Entity *e = check_entity(L, 1);
    push_vec2(L, e->velocity.x, e->velocity.y);
    return 1;
}

static int entity_set_vel(lua_State *L) {
    Entity *e = check_entity(L, 1);
    Vec2 *v   = check_vec2(L, 2);
    e->velocity = *v;
    return 0;
}

static int entity_is_alive(lua_State *L) {
    Entity *e = check_entity(L, 1);
    lua_pushboolean(L, e->active);
    return 1;
}

static int entity_kill(lua_State *L) {
    Entity *e = check_entity(L, 1);
    e->active = 0;
    return 0;
}

static int entity_tostring(lua_State *L) {
    Entity *e = check_entity(L, 1);
    lua_pushfstring(L, "Entity{tag=%s, pos=(%g,%g), active=%s}",
        e->tag, e->position.x, e->position.y,
        e->active ? "true" : "false");
    return 1;
}

/* __gc: GC 时自动调用 */
static int entity_gc(lua_State *L) {
    Entity *e = (Entity *)lua_touserdata(L, 1);
    /* 如果持有外部资源（如动态分配的内存、文件句柄等），在此释放 */
    (void)e;
    return 0;
}

static const luaL_Reg entity_methods[] = {
    {"update",  entity_update},
    {"get_pos", entity_get_pos},
    {"set_pos", entity_set_pos},
    {"get_vel", entity_get_vel},
    {"set_vel", entity_set_vel},
    {"is_alive",entity_is_alive},
    {"kill",    entity_kill},
    {NULL, NULL}
};

static void register_entity(lua_State *L) {
    luaL_newmetatable(L, ENTITY_MT);
    
    lua_pushvalue(L, -1);
    lua_setfield(L, -2, "__index");   /* mt.__index = mt */
    
    lua_pushcfunction(L, entity_tostring);
    lua_setfield(L, -2, "__tostring");
    
    lua_pushcfunction(L, entity_gc);
    lua_setfield(L, -2, "__gc");
    
    luaL_setfuncs(L, entity_methods, 0);
    lua_pop(L, 1);
}

/* ── 模块入口函数 ─────────────────────────────────────── */

static const luaL_Reg mylib_funcs[] = {
    {"Vec2",   vec2_new},
    {"Entity", entity_new},
    {NULL, NULL}
};

/* require("mylib") 的入口：luaopen_<模块名> */
int luaopen_mylib(lua_State *L) {
    /* 注册所有类型的 metatable */
    register_vec2(L);
    register_entity(L);
    
    /* 创建并返回模块表 */
    luaL_newlib(L, mylib_funcs);
    
    /* 添加常量 */
    lua_pushnumber(L, 1.0);
    lua_setfield(L, -2, "VERSION");
    
    /* 内置常用 Vec2 常量 */
    push_vec2(L, 0, 0);  lua_setfield(L, -2, "ZERO");
    push_vec2(L, 1, 0);  lua_setfield(L, -2, "RIGHT");
    push_vec2(L, 0, 1);  lua_setfield(L, -2, "UP");
    
    return 1;  /* 返回模块表 */
}

/*
 * Lua 使用示例:
 *
 *   local lib = require("mylib")
 *
 *   -- Vec2
 *   local v = lib.Vec2(3, 4)
 *   print(v:length())         -- 5.0
 *   print(v:normalize())      -- Vec2(0.6, 0.8)
 *   local a = lib.Vec2(1, 2)
 *   local b = lib.Vec2(3, 4)
 *   print(a + b)              -- Vec2(4, 6)
 *   print(a:dot(b))           -- 11.0
 *   v.x = 10                  -- 直接赋值
 *
 *   -- Entity
 *   local e = lib.Entity(100, 200, 16, "player")
 *   e:set_vel(lib.Vec2(50, 0))
 *   e:update(0.016)
 *   print(e:get_pos())        -- Vec2(100.8, 200)
 *   print(e)                  -- Entity{tag=player, pos=(100.8,200), active=true}
 */
