---
title: MVVM + Riverpod 实战
date: 2026-08-24
category: 架构思路
author: 阅读整理
draft: false
---


登录代码很容易从十几行长成一团：按钮置灰、调用接口、存凭据、更新用户、跳转首页，再给每一步补上异常处理。问题通常出在这些事情共享同一段异步流程，却没有明确谁负责收尾。

Riverpod 可以让状态离开页面，但换一个状态管理库，不会自动消除生命周期问题。

## 先分清后台和页面销毁

应用进入后台，不代表登录页已经从组件树卸载。真正危险的是 await 期间页面被关闭或替换，随后继续使用旧 context，或者对已销毁的 State 调用 setState。

对于简单页面，先做好生命周期判断就是有效修复：

```dart
final user = await repository.login(email, password);
if (!context.mounted) return;
// 此处再使用 context 更新导航或展示反馈。
```

这只保证 context 仍有效，不保证当前页面仍适合跳转，也不处理重复请求。失败分支和 finally 中的 UI 更新同样需要考虑页面是否存在。[BuildContext.mounted](https://api.flutter.dev/flutter/widgets/BuildContext/mounted.html)

## 拆分按职责，不按文件数量

Repository 负责认证接口和会话保存；登录控制器负责提交状态；页面负责输入和展示；应用级会话状态决定是否进入已登录区域。

如果路由已经由会话状态驱动，就不要在按钮回调和状态监听中再各跳一次。多个地方同时管理登录后的导航，往往比原来的 setState 更难排查。

提交状态可以分为 idle、submitting、success、failure。两个互不约束的布尔值 isLoading 和 isSuccess 容易产生“正在加载，同时已经成功”的组合。失败状态还应包含能给用户解释的信息，而不只是把 loading 关掉。

## AsyncNotifier 的初始状态也有含义

原文把 build 写成抛出 UnimplementedError，这不是可直接使用的登录初始状态。用户尚未提交时应该处于空闲状态，而不是初始化失败。

若用 AsyncValue 表达提交结果，必须明确初始 data(null) 代表尚未登录，不能把“出现 AsyncData”直接当成登录成功。若还要表达验证码、二次认证或账号选择，自定义状态通常更直观。

原文的 LoginState 也没有提供后续调用所需的 copyWith。示例适合说明拆分方向，不能整段复制后就认为实现完整。

## 页面离开后，请求结果还会回来

按钮禁用只能挡住当前 UI 的重复点击。控制器本身仍要避免重复提交；允许后一次覆盖前一次时，还要用请求序号或取消机制阻止旧结果回写。

Riverpod 3 提供 ref.mounted，异步间隙后可先判断 provider 是否仍存活；它和 context.mounted 检查的是不同对象。旧版本不能直接照搬这个 API。实际请求取消应在销毁回调里按所用网络库处理。[Riverpod 版本记录](https://pub.dev/packages/riverpod/changelog)

表单提交状态和应用会话也应分开考虑：离开登录页是否取消登录，是产品行为选择，不能偶然由 provider 的生命周期决定。

原文将缺少 ProviderScope 描述成热重载问题，还建议避免 provider 与 riverpod 共存。这些说法过于绝对。应先确认入口配置和异常来源；渐进迁移时可以共存，只要同一业务状态有明确归属。

验收时至少走一次：连续点击提交、请求中返回、失败后再次提交、成功后监听重复触发。比单独验证“能跳到首页”更能发现这次拆分是否有效。
