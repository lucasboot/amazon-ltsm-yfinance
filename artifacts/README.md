# Artifacts - Modelo e Scaler

Esta pasta deve conter os artefatos do modelo LSTM treinado.

## 📁 Arquivos Necessários

### 1. `amzn_lstm_model.keras`
- **Tipo:** Modelo TensorFlow/Keras
- **Formato:** `.keras` (formato recomendado do Keras 3.x)
- **Descrição:** Modelo LSTM treinado para predição de preços

**Como gerar:**
```python
# Após treinar seu modelo
model.save('artifacts/amzn_lstm_model.keras')
```

---

### 2. `scaler.save`
- **Tipo:** Scaler scikit-learn
- **Formato:** Arquivo joblib
- **Descrição:** Scaler usado para normalizar/desnormalizar dados

**Como gerar:**
```python
import joblib
from sklearn.preprocessing import MinMaxScaler

# Após treinar o scaler
scaler = MinMaxScaler()
scaler.fit(X_train)  # X_train com suas 5 features (OHLCV)

# Salvar
joblib.dump(scaler, 'artifacts/scaler.save')
```

## ✅ Verificação

Para verificar se os arquivos estão corretos:

```bash
# Listar arquivos
ls -lh artifacts/

# Deverá mostrar:
# amzn_lstm_model.keras (tamanho varia, tipicamente alguns MB)
# scaler.save (tipicamente alguns KB)
```

## 🔍 Validação em Python

```python
import tensorflow as tf
import joblib

# Carregar modelo
model = tf.keras.models.load_model('artifacts/amzn_lstm_model.keras')
print(f"Model input shape: {model.input_shape}")
print(f"Model output shape: {model.output_shape}")

# Carregar scaler
scaler = joblib.load('artifacts/scaler.save')
print(f"Scaler features: {scaler.n_features_in_}")

# Validações esperadas:
# - Input shape: (None, 60, 5) - 60 timesteps, 5 features
# - Output shape: (None, 1) - 1 valor de predição
# - Scaler features: 5 (open, high, low, close, volume)
```

## ⚠️ Importante para Deploy

- **Tamanho:** Certifique-se de que o modelo não é muito grande
  - Vercel Hobby: Limite de 50MB para todo o deployment
  - Vercel Pro: Limite de 100MB
  
- **Formato:** Use `.keras` (não `.h5`) para melhor compatibilidade

- **Versionamento Git:**
  - ⚠️ Não commite modelos muito grandes no Git
  - Considere usar Git LFS para arquivos grandes
  - Ou armazene em cloud storage e baixe durante CI/CD

## 📦 Alternativas de Storage

Se o modelo for muito grande para Git:

### Opção 1: Git LFS
```bash
# Instalar Git LFS
git lfs install

# Rastrear arquivos grandes
git lfs track "artifacts/*.keras"
git lfs track "artifacts/*.save"

# Commit
git add .gitattributes
git commit -m "Configurar Git LFS"
```

### Opção 2: Cloud Storage
- Google Cloud Storage
- AWS S3
- Azure Blob Storage

Baixe durante o build/startup da aplicação.

### Opção 3: Vercel Blob
Use Vercel Blob Storage para armazenar artefatos grandes.

## 🔄 Atualização de Modelo

Para atualizar o modelo em produção:

1. Substitua os arquivos na pasta `artifacts/`
2. Commit e push para o repositório
3. Vercel fará deploy automático
4. Cold start carregará o novo modelo

## 🆘 Troubleshooting

**Erro: "Modelo não encontrado"**
- Verifique se os arquivos estão nesta pasta
- Verifique permissões de leitura

**Erro: "Cannot load model"**
- Verifique compatibilidade de versão do TensorFlow
- Modelo foi salvo com TensorFlow 2.15.0
- Tente recriar o modelo com a versão correta

**Erro: "Scaler incompatível"**
- Verifique se o scaler foi treinado com 5 features
- Ordem das features deve ser: open, high, low, close, volume

