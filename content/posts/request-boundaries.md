---
title: 新增一个接口，不应该顺便重写一次网络请求
date: 2024-05-21
category: 架构思路
author: Wesley
excerpt: 把请求描述、业务协议和页面反馈分开，接口变多时才不会四处复制。
draft: false
---

一个项目刚开始时，直接在页面里调 Dio 很方便。等平台字段、语言、鉴权、业务码和缓存都加进来，新接口就变成了复制旧接口，再检查有没有漏改参数。

项目中的 `VMRequest → VMApi → VMResult → Service` 已经提供了不错的拆分起点。请求类描述要做什么，执行层负责发出去，Service 知道接口协议，页面处理交互结果。

这种结构最实在的收益，是调用处不再关心某个版本号请求头应该怎样填写。公共字段在 `onRequest` 里补齐，业务码在 `customAnalysis` 里解释。

### 同一张表单里的错误，也不一定用同一种提示

传输失败、字段不合法、会话失效，最后都可以表现为“请求没成功”，但页面处理方式不同。网络层如果直接弹 Toast，再由页面弹一次错误框，用户就会收到重复提示。

更合适的返回值是“已经解释过的事实”，而不是“已经执行过的 UI 动作”。下面是可用于新封装的结果形状，不是当前项目现成的类：

```dart
sealed class RequestResult<T> {}

final class RequestSuccess<T> extends RequestResult<T> {
  RequestSuccess(this.value);
  final T value;
}

final class RequestFailure<T> extends RequestResult<T> {
  RequestFailure(this.kind, this.message);
  final FailureKind kind;
  final String message;
}

enum FailureKind { network, timeout, unauthorized, business, decoding, cancelled }
```

这段使用 Dart 3。结果类型把取消、解析失败和业务拒绝保留下来，页面才能选择保留旧内容、提示重试，或者什么也不提示。

### Service 是协议的翻译位置

假设文章列表接口返回原始 Map，Service 应把它解析成文章列表后再交给页面。这里可以使用 `Future<RequestResult<List<Article>>>`，而不是让所有调用方继续理解嵌套的 `result` 字段。

也不必一次替换旧请求流。可以先在一个 Service 方法外包一层适配器，保留已有传输实现，等类型和异常约定稳定后再逐步迁移。

至于 Dio 是否使用单例，要看配置是否能够共享。当前实现每次创建实例，不能把它描述为连接复用方案。把生命周期与请求分层分别讨论，修改范围会更清楚。
