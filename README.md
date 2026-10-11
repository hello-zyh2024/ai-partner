# AI 智能伴侣

基于 Streamlit + DeepSeek 的流式对话应用，带人格设定和会话存档。

## 本地运行

```bash
pip install -r requirements.txt
export DEEPSEEK_API_KEY="你的密钥"   # Windows PowerShell: $env:DEEPSEEK_API_KEY="你的密钥"
streamlit run app.py
```

## 部署到 Streamlit Community Cloud

1. 打开 https://share.streamlit.io ，用 GitHub 账号登录。
2. 选择 **New app**，仓库选 `hello-zyh2024/ai-partner`，分支 `main`，Main file path 填 `app.py`。
3. 点 **Advanced settings → Secrets**，填入：

   ```toml
   DEEPSEEK_API_KEY = "你的密钥"
   ```

4. 点 **Deploy**。

应用优先读环境变量 `DEEPSEEK_API_KEY`，读不到再读 `st.secrets`，所以上面两种配置方式都可用。

## 说明

- `sessions/` 是运行时会话存档目录，Streamlit Cloud 的容器文件系统是临时的，重启后会清空。
- `.streamlit/secrets.toml` 已被 `.gitignore` 排除，不要提交密钥。
