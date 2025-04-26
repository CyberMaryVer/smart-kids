
kids = {
    "Arseniy": {
        "name": "Арсений",
        "emoji": "🧪",
        "title": "Инженер-волшебник",
        "description": "Гениальный строитель порталов и башен в роблокс или механизмов в майнкрафт, который решает химические уравнения быстрее, чем вы моргаете! Его светлый ум и добрый характер делают его настоящим магом науки. Арсений очень любознателен, настроен позитивно и всегда имеет в запасе кучу вопросов к миру."
    },
    "Kirill": {
        "name": "Кирилл",
        "emoji": "🎮",
        "title": "Стратег и дипломат",
        "description": "Виртуозный игрок Counter-Strike, Кирилл несомненно обладает и дипломатическим талантом! Лидерство его естественное состояние. Никто не умеет так мастерски управлять людьми и получать желаемое, как Кирилл со своим стратегическим мышлением. Воистину рыцарь, всегда встанет на защиту слабых и обладает большим бесстрашием."
    },
    "Uliana": {
        "name": "Ульяна",
        "emoji": "🎨",
        "title": "Художница перфекционистка",
        "description": "Её кисть творит чудеса, а организационные способности впечатляют даже взрослых! Изящная и решительная Ульяна видит красоту в деталях и упорядочивает хаос. Её аналитический ум постоянно препарирует реальность, а безупречный вкус превращает обыденность в шедевр."
    },
    "Sofia": {
        "name": "София",
        "emoji": "🌟",
        "title": "Эмпатичная бунтарка",
        "description": "Талантливая актриса с душой художницы и сердцем, способным чувствовать каждое движение чужой души! София обожает капибар, черный юмор и Алису в Пограничье. Её наблюдательность граничит с ясновидением, а чувство юмора прекрасно. Не любит учиться, но в школе у нее полно друзей."
    },
    "Miya": {
        "name": "Мия",
        "emoji": "👶",
        "title": "Маленькая покорительница мира",
        "description": "Самая юная и загадочная героиня! Несмотря на младенческий возраст, Мия демонстрирует невероятные упорство и позитив и с каждым днем открывает новые грани своего характера. Кто знает, какие таланты таятся в этой маленькой и решительной первооткрывательнице!"
    }
}

import streamlit as st
import os

# --- CSS for Customization ---
css_path = "style.css"
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    print(f"CSS file not found: {css_path}")

images_paths = {
    "Arseniy": "images/arseniy.png",
    "Kirill": "images/kirill2.png",
    "Uliana": "images/ulyana2.png",
    "Sofia": "images/sofia2.png",
    "Miya": "images/mia.png"
}

st.title("Наша команда")

for name, path in images_paths.items():
    person = kids[name]
    st.markdown(f"<h2>{person['title']}</h2>", unsafe_allow_html=True)

    # Create two columns
    col1, col2 = st.columns((1, 5), gap="small")

    with col2:
        st.markdown(f"""
        <div class="character-card character-arseniy">
            <div class="character-name"><span class="character-avatar">{person['emoji']}</span>{person['name']}</div>
            <p>{person['description']}</p>
        </div>
        """, unsafe_allow_html=True)

    with col1:
        # image
        st.image(path, width=200)

