# 第2阶段说明
# 本节课程：Reducer函数机制

## 学习目标
1. 理解Reducer函数的作用和原理
2. 掌握如何使用Annotated和operator.add定义Reducer
3. 理解不同Reducer对状态更新行为的影响

## 核心概念
- Reducer函数：根据给定输入（当前状态和操作）生成新的状态
- Annotated：Python类型提示工具，用于添加额外元数据
- operator.add：列表拼接操作，将新值追加到现有列表

## 课程文件
- 01_Reducer机制原理.py：演示默认覆盖操作
- 02_Annotated定义Reducer.py：使用Annotated和operator.add

## 注意事项
- 默认情况下，State中的key使用覆盖操作更新
- 通过Annotated可以指定自定义Reducer函数