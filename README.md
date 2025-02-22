# pdf_summary
## RAGをDjangoで使う方法を学びたくて作ったものです。
## 環境変数の設定
使用の際はプロジェクト直下に.envファイルを作成し、以下の変数を定義してください
- OPENAI_API_KEY={openAIのAPIキー}
- LANGCHAIN_API_KEY={LangchainのAPIキー}
- OPENAI_API_BASE={openAIのエンドポイント}
- SECRET_KEY={DjangoのSECRET_KEY}

## コードの説明
本プロジェクトは、OpenAI API と Langchain を使用して、PDF の要約および質問応答を行うツールです。
指定した PDF ファイルの内容を解析し、要点を抽出したり、特定の質問に対して回答を生成することができます。
フレームワークとしてDjangoを用いています

## 主要なインポート
- pip install Django
- pip install django-environ
- pip install --quiet --upgrade langchain langchain-community langchain-chroma
- pip install -qU langchain-openai
- pip install PyMuPDF<br>
足りないものがあった場合は追加でimportして下さい(仮想環境はvenvを使用)



## 著作権に関する注意 (Copyright Notice)
本ソフトウェアは、PDFの内容を解析・検索するためのツールです。  
**著作権のあるPDFを扱う際は、使用者の責任で適切に取り扱ってください。**  
特に、**第三者に解析結果を提供する場合や、商用利用を行う場合は、必ず著作権者の許可を得てください。**  
**違法行為への利用は禁止** です。  


## 免責事項 (Disclaimer)
本ソフトウェアは **現状のまま (AS IS)** 提供されます。  
本ソフトウェアを使用したことによる **いかなる損害についても、開発者は責任を負いません**。  
自己責任でご利用ください。

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,  
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE  
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,  
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,  
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
