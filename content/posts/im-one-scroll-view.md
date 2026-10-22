---
title: 聊天列表套两层滚动，方便的是布局，麻烦的是后面
date: 2025-01-16
category: 组件设计
author: Wesley
excerpt: 从现有嵌套结构收敛到一个可滚动视口，但迁移时别丢掉定位能力。
draft: false
---

项目把一个禁止滚动、`shrinkWrap: true` 的 ListView 放进反向 SingleChildScrollView。外层负责滚动，内层负责消息和间隔，结构上很好理解。

这种组合适合内容不多、整体高度容易计算的页面。聊天记录不断增加以后，内部列表为了确定自身尺寸需要付出更多布局工作，原本期待的按视口组织长列表的收益也会被削弱。这里不能只凭源码说“掉帧多少”，但继续增长的布局成本值得关注。

可以先把日期、消息、未读提示整理成一组行，再让一个 ListView 同时负责构建和滚动：

```dart
// rowsNewestFirst 已按最新展示行在前排列。
// rowBuilder 只根据这一行的数据生成 Widget。
ListView.builder(
  controller: scrollController,
  reverse: true,
  itemCount: rowsNewestFirst.length,
  itemBuilder: (context, index) {
    final row = rowsNewestFirst[index];
    return KeyedSubtree(
      key: ValueKey(row.stableKey),
      child: rowBuilder(context, row),
    );
  },
)
```

这是接入片段，`stableKey` 和 `rowBuilder` 由展示行模型提供。父布局需要给列表有限高度，例如放在 Column 的 Expanded 中；否则只是把一种布局问题换成另一种。

### 一个视口，才能统一讨论滚动位置

历史加载监听谁，新消息跟随谁，引用定位滚动谁，这些问题最好对应同一个实际 ScrollPosition。项目里两个控制器都接触同一滚动控制器，重构时应确定一个入口负责滚动策略，避免重复监听、重复加载。

稳定 key 能帮助框架识别行，但它不是自动保持阅读位置的开关。插入历史、图片变高、键盘出现，都可能需要额外的锚点或视口策略。

### 懒构建会影响引用定位

现有引用定位依赖消息的 GlobalKey 和 `ensureVisible`。收敛为按需构建的列表后，远处的消息可能没有对应的已挂载组件，`currentContext` 会为空。

因此，不能只替换列表就宣布重构完成。还要决定按索引定位、分段加载定位，或者先把目标移动到构建区域，再做精确对齐。列表性能和定位能力需要一起设计。

实际验证时，可以准备包含文本、长图、语音与日期行的长会话，观察快速滑动、加载历史、返回最新消息三个动作。布局结构更简单是收益，体验是否改善还要在设备上确认。
