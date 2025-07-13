# 地震データ可視化アプリ / Earthquake Data Visualizer

このアプリは、USGS の地震データ API を利用して日本周辺の地震情報を可視化します。  
This app visualizes earthquake data around Japan using the USGS Earthquake API.

---

## 🛠️ 使い方（ローカル実行） / How to Run Locally

### 1. リポジトリをクローン / Clone the Repository

```bash
git clone https://github.com/kitakazex/earthquake-visualizer.git
cd earthquake-visualizer
```

### 2. 仮想環境の作成（推奨） / Create a Virtual Environment (Recommended)

```bash
# Python 3.8+ がインストールされている必要があります
# Python 3.8+ must be installed
python -m venv venv
```

### 3. 仮想環境をアクティベート / Activate the Virtual Environment
- Windows

```bash
.\venv\Scripts\activate
```
- macOS/Linux

```bash
source venv/bin/activate
```
### 4. 依存パッケージをインストール / Install Dependencies
```bash
pip install -r requirements.txt
```
### 5. アプリを起動 / Run the App
```bash
streamlit run app.py
```
## 💡 補足 / Notes
- 仮想環境を利用することで、他の Python プロジェクトとの依存関係の競合を防ぐことができます。
Using a virtual environment helps prevent dependency conflicts with other Python projects.

- Streamlit を初めて使う場合は、実行後に表示される URL（通常は `http://localhost:8501`）をブラウザで開いてください。
If you're new to Streamlit, open the displayed URL (usually `http://localhost:8501`) in your browser after running.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://earthquake-visualizer-yhys4qb9ubapzmpatdqdcm.streamlit.app/)
