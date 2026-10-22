---
title: 聊天列表里插日期，不要在 itemBuilder 里数消息
date: 2024-11-07
category: 交互实现
author: Wesley
excerpt: 先把消息整理成展示行，再交给列表渲染，索引关系会清楚很多。
draft: false
---

一段聊天里有文字、有图片，中间还要插“昨天”“今天”。最容易想到的做法，是先算出哪些索引需要日期，再在 `itemBuilder` 里用一个计数器跳过它们。

项目的 `MyChatListView` 就用了类似结构：先建立日期分隔位置，再用 `count` 把列表索引换算回消息索引。短列表初看没有问题，但 builder 应该能独立处理任意索引。某一项因为布局变化重新构建时，不该依赖此前恰好调用过几次。

更容易推敲的办法，是在构建列表前把消息转换成展示行。日期行也是一行，不再是索引计算中的特殊情况。

下面是一个最小的数据整理示例，使用 Dart 3。输入已经按时间升序排列，时间已转换到统一的展示时区：

```dart
class TimelineMessage {
  const TimelineMessage(this.id, this.sentAt);
  final String id;
  final DateTime sentAt;
}

sealed class TimelineRow {}

class DayRow extends TimelineRow {
  DayRow(this.day);
  final DateTime day;
}

class MessageRow extends TimelineRow {
  MessageRow(this.message);
  final TimelineMessage message;
}

List<TimelineRow> buildRows(List<TimelineMessage> messages) {
  final rows = <TimelineRow>[];
  DateTime? previousDay;
  for (final message in messages) {
    final time = message.sentAt;
    final day = DateTime(time.year, time.month, time.day);
    if (day != previousDay) {
      rows.add(DayRow(day));
      previousDay = day;
    }
    rows.add(MessageRow(message));
  }
  return rows;
}
```

此后 builder 只需要读取 `rows[index]`，根据类型返回日期组件或气泡。重复调用某个索引，结果不会受到之前构建顺序影响。消息行的 key 使用稳定消息标识，日期行使用独立命名空间，避免两类 key 冲突。

### 先整理正序，再决定怎么展示

收到历史数据时，最好先统一排序和去重，再生成日期行。日期判断使用展示时区，不能一部分消息用 UTC、一部分用设备本地时间，否则跨日位置会不一致。

若最终使用 `reverse: true` 的单层 ListView，让最新行位于 index 0，可以把已经整理好的整组展示行反转。不要只反转消息、不处理日期分隔，否则日期标签会跑到错误的一侧。

聊天的未读分割线、加载提示也可以用同样的方法加入展示行。先把“这一行是什么”确定下来，滚动组件就不必参与业务索引运算。
