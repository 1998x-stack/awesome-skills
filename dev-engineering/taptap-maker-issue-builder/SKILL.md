---
name: taptap-maker-issue-builder
description: format, rewrite, and route taptap maker and 一方游戏 group issue reports into concise, actionable problem statements. use when the user provides raw bug reports, customer complaints, payment/order problems, build failures, publish issues, asset problems, ai experiment/research discussions, game design/development blockers, agent/runtime failures, permission questions, or messy chat context and wants a high-signal slack message, issue card, escalation note, collaboration request, or problem summary for taptap maker collaborators.
---

# TapTap Maker Issue Builder

## Purpose

Turn noisy TapTap Maker / 一方游戏 problem context into a concise, respectful, actionable issue report. Prioritize reader efficiency: start with the problem and the required help, then list only evidence that helps the assignee verify, reproduce, or decide.

## Core principle

Always produce the report in this order:

1. **One-sentence ask**: state the issue, impact, who needs to help, and the expected resolution or decision.
2. **Evidence and context**: list concrete facts, IDs, screenshots, timestamps, status, user request, experiments already run, and what has already been checked.
3. **Open questions**: explicitly mark missing fields or uncertain ownership instead of hiding ambiguity.

Avoid dumping background, emotional commentary, full process history, or broad taxonomy maps unless the user explicitly asks for a postmortem or knowledge map.

## Default workflow

1. Identify the issue type: payment/order/refund, publish/build, agent/runtime, rollback/history, asset/upload/media, mobile/adaptation, debug/logs, workflow/ux, permission/whitelist, compliance/security, AI experiment/research, game design/content, game development/testing, infrastructure/ops, or unknown.
2. Pick a likely owner using `references/routing-map.md` only when ownership is clear.
   - If the input mentions `一方游戏`, named games such as `脑力大冒险` / `故事世界` / `闯天关：大闹天宫` / `挂机大亨`, or the newer 一方游戏 member list, consult `references/yifang-game-routing-map.md`.
   - If ownership is uncertain, say `协助人待定` and ask the current channel to help route.
3. Extract high-signal fields from the user input. Preserve IDs, amounts, project names, error messages, model names, timestamps, and quoted user statements exactly.
4. Remove irrelevant internal process, repeated descriptions, and anything that does not help locate, verify, reproduce, or resolve the issue.
5. Select the most appropriate template: normal issue report, payment/refund, build/publish/runtime, or research/collaboration request.
6. Run the quality gate before finalizing.

## Owner selection rules

Use the routing maps as routing assistance, not as content to paste into the final answer.

1. Prefer the person who can unblock the next action fastest.
2. Prefer explicit evidence over generic role labels.
3. If a responsibility is marked as inferred, tentative, or citation-missing, use softer wording such as `建议先 @... 看看` or list the person under `cc / 待确认`, not as a definitive owner.
4. Do not tag too many people. Default to one primary owner plus at most two cc names.
5. If the issue is a cross-domain discussion, separate `主协助` and `可 cc`.

## Default Slack template

```markdown
[一句话问题 / 需要协助]：@[协助人] [对象/用户/项目] 在 [场景] 遇到 [问题]，请协助 [查证/确认/修复/退款/补发/开权限/判断归属]。

【用户问题 / 现象】：...
【用户诉求】：...
【影响范围 / 优先级】：...
【关键时间】：...
【商品 / 项目 / 服务】：...
【关键 ID】：
- 用户 / 昵称 / UID：...
- TapTap 交易号 / 订单号：...
- 外部交易号：...
- 商家名称 / ID：...
- 项目 / 应用 / 包名 / 版本：...
【当前状态 / 已查证】：...
【附件 / 证据】：截图、日志、链接、报错文本等
【待确认】：...
```

Only keep fields that are useful for the specific case. If an important field is missing, include it under `【待确认】` instead of inventing it.

## Payment/refund special template

Use this for duplicated payment, paid-but-service-not-received, redemption-code purchase, refund, order, or Alipay issues.

```markdown
[一句话问题 / 需要协助]：@[协助人] 用户在 TapTap 购买/兑换「[商品名]」时出现「[核心问题]」，请协助确认 [交易归属/退款路径/补发服务/是否需要联系用户授权]。

【用户问题】：...
【用户诉求】：...
【交易号】：...
【外部交易号】：...
【总金额】：...
【商品 / 服务名称】：...
【商家名称 + ID】：...
【支付方式 / 状态】：...
【已查证】：...
【待确认】：...
```

For payment privacy: keep only necessary transaction identifiers and authorization status. Do not add phone numbers, real names, or unrelated personal information unless the user explicitly provides and requires it for the workflow.

## Build/publish/runtime special template

Use this for publish failures, build timeout, OOM, black screen, flashback, runtime crash, agent failure, rollback, or asset loading issues.

```markdown
[一句话问题 / 需要协助]：@[协助人] [项目/用户] 在 [发布/构建/运行/回滚] 时出现 [错误/现象]，请协助 [定位原因/恢复状态/修复/给出规避方案]。

【现象】：...
【复现路径】：...
【项目 / 应用 / 版本】：...
【发生时间】：...
【错误信息 / 日志】：...
【环境】：浏览器、系统、移动端、网络、模型、构建机等
【已尝试 / 已排除】：...
【影响】：阻塞发布、无法继续创作、影响单个用户/多个用户等
【待确认】：...
```

## Research/collaboration request template

Use this when the raw input is not a bug report but a messy discussion about AI experiments, benchmark design, game task construction, product exploration, or cross-role collaboration.

```markdown
[一句话问题 / 需要协助]：@[主协助人] 我想验证/推进 [目标]，目前卡在 [核心阻塞]，请协助 [给方案/构造样本/判断可行性/提供案例/确认 owner]。

【目标】：...
【当前方案】：...
【已做实验 / 结果】：...
【当前判断】：...
【需要协助】：
1. ...
2. ...
3. ...
【理想样本 / 验收标准】：...
【待确认】：...
【可 cc】：...
```

For research requests, avoid making the message sound like a confirmed bug. Clearly separate hypothesis, observed result, and requested help.

## Routing rules

Use `references/routing-map.md` and `references/yifang-game-routing-map.md` when the user asks who should look at the issue or when a message needs a direct @ mention. If the issue has multiple possible owners, mention the primary owner first and list secondary owners in `【待确认】` or `【可 cc】`.

Do not over-route. If the evidence is insufficient, write the first sentence as `协助人待定：...，请熟悉该模块的同学帮忙确认归属。`

## Quality gate

Before finalizing, check:

- The first sentence contains **what happened / what is being decided**, **who should help**, and **what action is needed**.
- The message can be understood without reading the raw chat history.
- Every included detail helps verify, reproduce, route, decide, or resolve the issue.
- Long background, broad problem maps, repeated explanations, and low-signal process text are removed.
- IDs, amounts, names, game names, model names, timestamps, and error messages are preserved exactly as provided.
- Hypotheses are labeled as hypotheses; observed results are labeled as observed results.
- Unknowns are explicit and not guessed.
- The tone is direct, factual, and respectful.

## Examples

See `references/examples.md` for good and bad patterns.
