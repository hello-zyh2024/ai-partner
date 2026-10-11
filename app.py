import streamlit as st
import os
from openai import OpenAI
import datetime
import json


# 读取 DeepSeek API Key：优先环境变量，其次 Streamlit Secrets
def get_api_key():
    key = os.environ.get('DEEPSEEK_API_KEY')
    if key:
        return key
    try:
        return st.secrets['DEEPSEEK_API_KEY']
    except Exception:
        return None


# 生成会话标识
def generate_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 保存会话信息函数
def save_session():
    if st.session_state.current_session:
        # 1.保存当前会话信息
        session_data = {
            'nick_name': st.session_state.nick_name,
            'nature': st.session_state.nature,
            'messages': st.session_state.messages
        }
        # 如果sessions目录不存在，则创建
        if not os.path.exists('sessions'):
            os.makedirs('sessions')
        # 2.保存当前会话信息到sessions目录下
        with open(f'sessions/{st.session_state.current_session}.json', 'w', encoding='utf-8') as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)


# 加载所有的会话列表
def load_sessions():
    sessions = []
    if os.path.exists('sessions'):
        for file in os.listdir('sessions'):
            if file.endswith('.json'):
                sessions.append(file[:-5])
    return sessions


# 设置页面的配置项
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🧊",
    # 布局
    layout="wide",
    # 控制侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.itcast.cn',
        'Report a bug': "https://www.itcast.cn",
        'About': "张远航真是个天才"
    }
)
# 大标题
st.title("AI智能伴侣")
# logo（st.logo 只接受图片路径或 URL，不能传 emoji）
if os.path.exists('uestc.jpg'):
    st.logo('uestc.jpg')
# 初始化聊天信息
if 'messages' not in st.session_state:  # 页面重跑（return）时普通变量会被重置，st.session_state可以理解为一个负责记忆的类字典容器
    st.session_state.messages = []
# 昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = '洛天依'
# 性格
if 'nature' not in st.session_state:
    st.session_state.nature = '温柔可爱'
# 会话标识
if 'current_session' not in st.session_state:
    st.session_state.current_session = generate_session_id()
# 系统提示词
system_prompt = f'你是AI助理，你的名字叫{st.session_state.nick_name}，请你使用{st.session_state.nature}的性格来回答用户的问题'
# 展示以前的聊天信息
for message in st.session_state.messages:  # {"role":"user","content":"prompt"}
    st.chat_message(message["role"]).write(message["content"])
# 创建与AI大模型交互的客户端对象
api_key = get_api_key()
if not api_key:
    st.error('未检测到 DEEPSEEK_API_KEY。请在 Streamlit 后台 Settings → Secrets 中配置，'
             '或在本机设置同名环境变量。')
    st.stop()
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com")
# 左侧的侧边栏--with:上下文管理器
with st.sidebar:
    st.subheader('AI控制面板')
    # 新建会话
    if st.button('新建会话', width='stretch', icon='🧊'):
        # 1.保存当前会话信息
        save_session()
        # 2.创建新的会话
        if st.session_state.messages:
            st.session_state.messages = []
            st.session_state.current_session = generate_session_id()
            save_session()
            st.rerun()  # 重新加载页面
    # 伴侣信息
    st.subheader('伴侣信息')
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature
# 消息输入框
prompt = st.chat_input('请输入您要问的问题：')
if prompt:
    st.chat_message('user').write(prompt)
    print('调用AI大模型，提示词:', prompt)
    # 添加用户发送的消息到聊天信息列表中
    st.session_state.messages.append({"role": "user", "content": prompt})
    # 调用AI大模型
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
        stream=True,
        extra_body={"thinking": {"type": "disabled"}}  # 禁用思维链
    )
    # 流式输出的解析方式（不带思维链）
    response_message = st.empty()  # 创建一个空的聊天消息容器，用于显示大模型的返回结果
    full_response = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None and chunk.choices[0].delta.content != "":
            content = chunk.choices[0].delta.content
            full_response += content
            response_message.chat_message('assistant').write(full_response)
    # 添加大模型返回的结果到聊天信息列表中
    st.session_state.messages.append({"role": "assistant", "content": full_response})
