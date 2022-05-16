client:
    server主动消息中有json格式的Game信息，用于更新client中的Game对象
    宝石商人用json序列化Game对象，其他游戏可自定义。需继承Game类重载info_on_board, update_board

Server:
    所有游戏逻辑均在server实现，每个move之后调用info_on_board得到的信息发送给client，client调用update_board更新，并展示
    game move中 raise ValueError 代表指令有误或执行的游戏指令不符合游戏规则
        raise RuntimeError或其他 表示游戏出现严重错误必须结束