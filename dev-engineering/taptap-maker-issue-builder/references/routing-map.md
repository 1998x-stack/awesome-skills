# TapTap Maker routing map

Use this map only for TapTap Maker issue triage and Slack-ready escalation. Prefer the clearest primary owner; add secondary owners only when the issue crosses domains.

If the issue is clearly from the `一方游戏` group, a named game project, game content production,版号游戏, AI benchmark task construction, or the newer member list provided by the user, consult `yifang-game-routing-map.md` first.

## Payment, order, refund, redemption

- Duplicated payment, paid-but-service-not-received, refund path, redemption-code vs direct-purchase distinction: `@陈一豪(cyh)` when the issue context matches the payment/order case shown by the user.
- If user authorization is required before looking up transaction details, state that explicitly in `【待确认】`.

## Product, requirements, operations

- Product requirements, iteration design, publish-panel optimization, SkillHub planning, requirement docs, cross-team coordination: `赵天一`.
- Points system, package configuration, user benefits, points query, campaign configuration, station-message notification: `丁帅`.
- Task tracking, requirement pool, PM coordination, document organization: `土豆儿（机器人）`.

## Server, backend, infrastructure

- Server architecture, MCP service, database, container deployment, account permission, environment setup, service expansion, API/performance: `王禹繁`.
- Server deployment, CI/CD, cloud resources, migration, container optimization: `王浩宇`.
- Game server, save system, serverCloud/clientCloud design, account isolation, data encryption: `蒋翼龙` when the issue explicitly involves game server or cloud save.

## MCP tools, publishing tools, resources

- MCP tool development, publish-flow optimization, material generation, multilingual support, OSS/CDN/cache, async build, 3D asset generation API: `张嘉豪`.

## Frontend and UI

- Publish panel, material library, points page, frontend compatibility, performance, interaction logic, multi-device adaptation, animation effects: `朱冰晶`.
- UI design specs, UI systems, responsive layout, font/component conventions: `周淼` when the issue is design/spec driven.
- UI system technical fixes, scissor/scrollView.lua/source-level UI implementation: `卢岚` when the issue mentions these implementation details.

## Engine, client, build/runtime

- UrhoX engine, build tools, build timeout, resource loading, threading, Spine integration, physics collision, engine performance: `施佳豪`.
- Game packaging and compliance, APK/PC package, real-name verification, anti-addiction SDK, embedded update, skip download stage: `梅琪`.
- Engine testing, build-tool testing, log analysis, reproduction, async build/resource loading verification: `程序小湿`.

## AI development tools and generated content

- ai-dev-kit, skill templates, technical docs, AI-generated content optimization, 3D model/animation/state-machine guidance, model training, multiplayer-save Skill review: `林美辰`.
- AI model effect testing in game development such as GLM 5 or Kimi2.5: route by concrete game owner first, cc `林美辰` if the issue concerns tool/model evaluation methodology.

## Game design, development, testing

- Puzzle game `脑力大冒险`, level design, UI optimization, sound system expansion, push-box/match-3 rules, tower-defense pre-design/data tables: `魏钟坪`.
- Story game `故事世界`, narrative branches, save-system modification, dialogue system, collection/gallery, voice integration: `朱哲靖`.
- Card game `闯天关：大闹天宫`, card design, battle system, art optimization, balance/status/card effects, compliance/art purification: `刘晓阳`.
- Simulation/idle management game `挂机大亨`, numeric design, progression, commercialization, animal staff, museum planning, ad integration: `刘赢`.
- Game testing, multiplayer testing, bug reproduction, performance, UX feedback, compliance validation such as anti-addiction/real-name verification: `胡兆荣`.

## Art assets and pipeline

- Art assets, asset pipeline, 3D model retrieval, SVN hooks, asset sync, Elasticsearch database sync, MCP model upload/management: `谢明`.
- 3D animation, character actions, animation effects, AI-generated content iteration, jump actions, state-machine templates, skeleton/material adaptation: `雷晶鑫`.
- 3D resources, materials, model polish, import/adaptation, PBR material, anime/cartoon shader adaptation, 3D model effect validation: `方钰`.

## Code analysis, QA, regression

- UrhoX source analysis, project code analysis, performance bottleneck analysis, clipboard feature, persistent server optimization: `张全栈`.
- Automation testing, MCP tool testing, version regression, functional verification, points-system testing, publish-flow verification: `张涛`.
- Code development and bug fixing, UrhoX source modifications, skill development, engine docs: `大师`.

## Overall technical coordination

- Overall technical direction, cross-department resource coordination, key architecture decisions, critical code review, project risk, external resource coordination such as API key applications: `姜黎`.

## Routing fallback

If evidence points to more than one domain, use this order:

1. Current blocker owner: who can unblock the next action fastest.
2. System owner: who owns the failing component.
3. Product/PM owner: who can decide priority or expected behavior.

If still unclear, write `协助人待定` instead of guessing.
