---
title: 确认框关掉以后，业务代码才开始
date: 2024-01-17
category: 工具封装
author: Wesley
excerpt: 把弹窗当作一次返回选择的交互，比在按钮回调里塞完整业务流程更容易维护。
draft: false
---

确认框最初只有两颗按钮。后来加上不同文案、危险操作颜色、异步提交和失败提示，就容易长成一个参数越来越多的工具方法。

项目的 `DialogUtils` 已经把外观收拢起来：底部弹层共用安全区域、圆角和键盘处理，确认框共用按钮样式。进一步整理时，我会让通用确认框只回答一个问题：用户是否确认？

下面是一个独立的改写示例，需要 `material.dart`。与原实现不同，它返回明确结果，不在弹窗内部执行业务：

```dart
Future<bool> askConfirmation(
  BuildContext context, {
  required String title,
  String? description,
}) async {
  final result = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      title: Text(title),
      content: description == null ? null : Text(description),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(dialogContext).pop(false),
          child: const Text('取消'),
        ),
        FilledButton(
          onPressed: () => Navigator.of(dialogContext).pop(true),
          child: const Text('确定'),
        ),
      ],
    ),
  );
  return result ?? false;
}
```

点击遮罩或通过返回操作退出，也按未确认处理。关闭时使用弹窗自己的 context，避免把调用页的路由误当成需要关闭的对象。

调用方等待结果后再提交。若等待期间页面可能被移除，继续使用页面 context 前要检查 `mounted`；删除、付款等业务还应在调用方防止重复提交。

### 提交成功后才关闭，是另一种弹窗

有些输入弹窗需要展示提交进度，服务拒绝后还要留在原地修改。这时就不要复用“先关闭、后执行”的确认框。让它成为有 `submitting` 和错误状态的独立组件，提交成功后再返回结果。

项目现有 `defaultDialog` 的按钮会先 `Get.back()`，再触发同步回调。它适合前一种交互，不会自动等待 Future。另外，原方法的 `content` 展示代码已被注释，保留参数并不代表正文真的会出现；重写时要同时清理接口与实现。

底部选择器也可以沿用返回值思路：返回被选中的项，取消返回空值。样式由封装统一，保存设置、发请求、跳转页面仍留在调用处，代码会少很多跨层依赖。
