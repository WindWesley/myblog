---
title: 给 List 加方法之前，先想清楚它会不会改原数据
date: 2023-07-19
category: 工具封装
author: Wesley
excerpt: 同样是少写一个循环，有些扩展让代码更清楚，有些只是把副作用藏了起来。
draft: false
---

把一组对象转成标题、给列表加序号、从空列表里取第一项，这些操作在业务代码里很常见。项目的 `ListEx` 把它们收成了扩展，调用处确实短了不少。

不过，扩展写得顺手之后，很容易把“少写几行”当成唯一标准。比如 `joinedByElements`，看名字像是产生一个带分隔元素的新列表，实际却在原列表上不断 `insert`，最后返回自身。拿它处理一次临时数据没问题；拿它处理共享列表，第二次调用就可能再插一遍。

我更倾向于让名字直接说明行为：修改原数据的方法使用 `insert`、`remove`，生成新数据的方法使用 `to`、`mapped`。如果是给 UI 列表加分隔项，可以重新构造结果：

```dart
extension ListHelpers<E> on List<E> {
  List<E> separatedBy(E Function(int gap) separator) {
    final result = <E>[];
    for (var i = 0; i < length; i++) {
      if (i > 0) result.add(separator(i - 1));
      result.add(this[i]);
    }
    return result;
  }
}

final source = ['甲', '乙'];
final display = source.separatedBy((_) => '·');
// display: [甲, ·, 乙]；source 仍然是 [甲, 乙]。
```

这里复制的是列表结构，里面的对象仍然共享；它不是深拷贝。这一点比“链式调用很优雅”更值得写进方法说明。

### 异步 map，名字里最好体现顺序

项目的 `futureMapWithIndex` 在循环中逐项 `await`。处理上一项结束后才开始下一项，结果保持输入顺序；如果某一项抛出异常，后面的项不会继续执行。

这种串行方式适合有依赖关系的操作。例如先创建父记录，再处理它的子项。几张彼此独立的缩略图转换，则可能适合有限并发。

不要只把循环换成 `Future.wait` 就称作优化。它可以同时启动大量任务，任务数很大时会增加资源压力。串行、有限并发、全部并发，应由任务的约束决定。

### “try” 不意味着能兜住任何异常

v4 新增的 `tryWhere` 用 `try/catch` 包住 `where` 调用。但过滤谓词通常在遍历返回的 Iterable 时才执行，异常可能在方法返回以后出现。若方法承诺立即验证，就应在内部完成遍历；若保留惰性行为，就不要给调用方“已经捕获异常”的错觉。

工具类值得保留的，是那些反复出现、含义稳定的操作。能一眼看懂的标准库调用，不一定需要再取一个项目专属名字。
