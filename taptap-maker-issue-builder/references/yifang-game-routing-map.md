# 一方游戏 group routing map

Source note: this map is based on the user-provided Feishu Q&A summary of `一方游戏` group member responsibilities. Some entries were explicitly marked as inferred or citation-missing in the source text, so route conservatively when evidence is weak.

Use this map when a request mentions 一方游戏, TapTap Maker game production,版号游戏, named prototype/game projects, game-specific testing, or AI/game task construction.

## Routing confidence

- **High confidence**: the raw issue mentions a person, named game, module, or exact responsibility below.
- **Medium confidence**: the issue domain strongly matches a role but no named project/person appears.
- **Low confidence**: the source responsibility was marked as inferred or `引用：无直接职责描述`; use `可 cc` or `待确认` instead of definitive ownership.

## Core management and coordination

| Person | Route when the issue involves |
|---|---|
| 姜黎 | Overall technical direction, cross-department resources, UrhoX code analysis/architecture, server migration, multilingual方案, critical code review, project risk, external resources/API key application. |
| 赵天一 | Product requirements and iteration, publish panel, points system adjustment, SkillHub planning, developer testing coordination, requirement docs, cross-team coordination, build timeout/version-number bug tracking, version-number/版号/compliance process, packaging coordination, real-name verification coordination. |
| 土豆儿（机器人） | TapTap Maker PM work, requirement tracking, task management, document organization, requirement pool, task assignment, progress sync. |

## Technical development and engine maintenance

| Person | Route when the issue involves |
|---|---|
| 施佳豪 | UrhoX engine, build tools, performance tuning, build timeout, resource loading, multithreading, Spine animation, physics collision, 边玩边下, multilingual technical implementation. |
| 林美辰 | ai-dev-kit, skill templates, technical documentation, AI-generated 3D models/animation/state machines, AI tool guidance, model training, multiplayer-save Skill review. |
| 张嘉豪 | MCP tools, publish-flow optimization, material generation, multilingual support, OSS config, CDN refresh/cache, asset generation optimization, async build, 3D asset generation APIs. |
| 王禹繁 | Server architecture, MCP service, database, container deployment, fuping environment, account permission, service expansion, backend API design, performance optimization. |
| 朱冰晶 | Frontend implementation, publish panel, asset/material library, points page, frontend compatibility, performance, interaction logic, multi-end adaptation, animation effects. |

## Game development and content production

| Person | Route when the issue involves |
|---|---|
| 魏钟坪 | `脑力大冒险`, puzzle game development, level design, UI optimization, sound system expansion, push-box/match-3 rules, game logic/numeric balance, tower-defense early design, data tables, multiplayer-save testing/Skill docs. |
| 朱哲靖 | `故事世界`, story game development, plot design, branching narrative, save-system modification, dialogue system, collection/gallery, voice integration, GLM 5 / Kimi2.5 model effect testing, multiplayer-save testing/Skill docs. |
| 刘晓阳 | `闯天关：大闹天宫`, card game development, card design, battle system, art optimization, balance/numeric adjustment, damage priority, status effects, card VFX, version-number game compliance/art purification. |
| 刘赢 | `挂机大亨`, simulation/idle management development, numeric design, growth/progression, commercialization module, animal staff system, museum planning, ad integration, compliance and numeric adjustment. |
| 胡兆荣 | Game testing and feedback, multiplayer testing, bug reproduction, performance optimization, UX issues, control convenience, layout, sound adaptation, version-number game compliance testing such as anti-addiction and real-name verification. |

## Art and UI design

| Person | Route when the issue involves |
|---|---|
| 雷晶鑫 | 3D animation/model development, character actions, animation optimization, AI-generated content iteration, jumping action, state-machine templates, skeleton binding, material adaptation. |
| 方钰 | 3D resources/materials, model polish, material configuration, resource import, 3D model testing/adaptation, PBR materials, anime/cartoon shader adaptation. |
| 周淼 | UI design and specifications, casual/cartoon UI systems, UI docs/templates, responsive layout, font specs, component libraries, AI UI generation validation. |
| 谢明 | Art assets and pipeline, 3D model search/retrieval, SVN hooks, asset sync, Elasticsearch database sync, art asset workflow optimization, MCP model upload/management modifications. |

## Testing and operations

| Person | Route when the issue involves |
|---|---|
| 梅琪 | Game packaging and compliance, APK/PC packaging, real-name verification, anti-addiction SDK integration, version release/update, embedded update, skip-download-stage optimization, packaging/compliance validation. |
| 程序小湿 | Engine testing, build-tool testing, log analysis, bug reproduction, async build validation, resource loading optimization validation. |
| 大师 | Code development and bug fixing, UrhoX source changes, skill development, engine docs. |
| 张涛 | Automation testing, MCP tool testing, version regression, feature verification, points-system testing, publish-flow verification. Source confidence: low-to-medium because the source text says no direct responsibility citation. |
| 王浩宇 | Infrastructure and operations, server deployment, CI/CD, cloud resources, service migration, container optimization. Source confidence: low-to-medium because the source text says no direct responsibility citation. |

## Other support roles

| Person | Route when the issue involves |
|---|---|
| 卢岚 | UI system technical fixes, unified `nvgIntersectScissor`, UI docs/spec maintenance, `scrollView.lua` source fixes. |
| 李佳洛 | Cursor/game development tool usage discussion and troubleshooting. |
| 蒋翼龙 | Game server and save system, `serverCloud` / `clientCloud`, user permission, account isolation, data encryption. |
| 张全栈 | UrhoX source/project code analysis, performance bottleneck analysis, clipboard feature, persistent server optimization. |

## Common cross-domain routing

- **AI experiment / benchmark / stable-failure dataset for TapTap Maker game tasks**: primary `林美辰` for AI/tool methodology; cc `赵天一` for product/task framing; cc a specific game owner such as `魏钟坪` / `朱哲靖` / `刘晓阳` / `刘赢` if the sample task is game-specific.
- **Game task construction requiring planning/design input**: primary the relevant game owner; cc `赵天一` if product priority or project direction is needed.
- **Build fails during game/package delivery**: primary `施佳豪` for engine/build-tool issues; cc `梅琪` if packaging/compliance/release is involved; cc `程序小湿` if reproduction/log analysis is needed.
- **Publishing or material-generation tool issue**: primary `张嘉豪`; cc `王禹繁` if backend/MCP service is involved; cc `朱冰晶` if frontend UI is involved.
- **Game server/save data/security issue**: primary `蒋翼龙`; cc `王禹繁` for backend platform/MCP service; cc `胡兆荣` if test reproduction is required.
- **Art pipeline / 3D asset issue**: primary `谢明`; cc `雷晶鑫` for animation/action/state-machine issues; cc `方钰` for material/model polish/adaptation.
- **UI spec vs implementation issue**: primary `周淼` for design/spec; primary `朱冰晶` for frontend implementation; cc `卢岚` if low-level UI implementation details such as scissor/scrollView are mentioned.

## Do not overstate certainty

When producing the final Slack-ready message, do not say `一定是 X 负责` unless the raw input explicitly proves it. Prefer:

- `建议先 @X 看看...`
- `主协助建议 @X；如果涉及 Y，可能需要 cc @Z`
- `协助人待定，请熟悉该模块的同学帮忙确认归属`
