client:
    server主动消息中有json格式的Game信息，用于更新client中的Game对象
    宝石商人用json序列化Game对象，其他游戏可自定义。需继承Game类重载 state, set_state

Server:
    所有游戏逻辑均在server实现，每个move之后调用 state() 得到的信息发送给client，client调用 set_state 更新，并展示