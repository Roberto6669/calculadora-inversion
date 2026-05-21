# Cómo actualizar las tasas de los fondos

Manual paso a paso para cambiar las tasas de FELAX, FKDNX y VADAX
en la calculadora de inversión y publicar los cambios en Render.

---

## Tasas actuales

| Fondo  | Nombre completo              | Tasa actual |
|--------|------------------------------|-------------|
| FELAX  | Fidelity Adv Semiconductors A | 35.29%      |
| FKDNX  | Franklin DynaTech A           | 17.87%      |
| VADAX  | Invesco Diversified Dividend A | 11.38%     |

---

## Pasos

### 1. Entrar a la carpeta y bajar los últimos cambios

```
cd ~/Library/Mobile\ Documents/com~apple~CloudDocs/__DATA/_AI/calculadora-inversion
git pull
```

### 2. Ver las tasas actuales en el archivo

```
grep "fund-rate" index.html
grep "usarFondo" index.html
```

Deben aparecer 6 líneas en total: 3 con el porcentaje visible en la tarjeta,
y 3 con el número del botón "Usar esta tasa".

### 3. Cambiar las tasas con sed

⚠️ IMPORTANTE — En Mac es `sed -i ''` con las dos comillas simples vacías.
⚠️ La tasa vieja lleva backslash en el punto (`35\.29`). La nueva NO.

Cambia los números VIEJOS y NUEVOS por los reales:

```
sed -i '' 's/35\.29/NUEVA_FELAX/g' index.html
sed -i '' 's/17\.87/NUEVA_FKDNX/g' index.html
sed -i '' 's/11\.38/NUEVA_VADAX/g' index.html
```

### 4. Verificar que el cambio quedó bien

```
grep "fund-rate" index.html
grep "usarFondo" index.html
```

Deben aparecer las tasas NUEVAS.

Verificar que las VIEJAS ya no quedaron pegadas en ningún lado:

```
grep -c "35.29" index.html
grep -c "17.87" index.html
grep -c "11.38" index.html
```

Los tres deben responder `0`.

### 5. Esperar a iCloud

Antes de hacer `git push`, mira en Finder que la carpeta NO tenga
el ícono de nube con flechas circulares. Espera a que termine la
sincronización de iCloud (unos segundos).

### 6. Subir los cambios a GitHub

```
git add index.html
git commit -m "Actualizar tasas: FELAX X.XX, FKDNX X.XX, VADAX X.XX"
git push
```

(Reemplaza los X.XX por los números reales en el mensaje)

### 7. Esperar el rebuild en Render

En ~1 minuto, Render detecta el push y reconstruye automáticamente.
Verifica abriendo tu URL pública en el navegador.

---

## Después de actualizar — IMPORTANTE

1. Actualiza la **tabla de tasas actuales** al inicio de este archivo
   con los nuevos números, para que la próxima vez sepas de qué a qué cambiar.
2. Sube también este archivo al commit:

```
git add ACTUALIZAR-TASAS.md
git commit -m "Actualizar tabla de referencia"
git push
```

---

## Si algo sale mal

**"fatal: not a git repository"** — iCloud probablemente corrompió la
carpeta `.git`. Avísame y te ayudo a recuperar desde GitHub.

**`sed` me da error** — revisa que tengas las dos comillas simples vacías
después del `-i`: `sed -i '' '...'` y no `sed -i '...'`.

**El `grep -c` no me da 0** — significa que la tasa vieja aparece en otro
lado del archivo (quizás en una fecha, un año, etc.) y `sed` cambió cosas
que no debía. Avísame antes de hacer `git push`.

**El push pide usuario y contraseña** — usuario es `Roberto6669`, y la
"contraseña" es tu Personal Access Token de GitHub (el mismo de fund-viz-app).
