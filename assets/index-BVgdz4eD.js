(function(){let e=document.createElement(`link`).relList;if(e&&e.supports&&e.supports(`modulepreload`))return;for(let e of document.querySelectorAll(`link[rel="modulepreload"]`))n(e);new MutationObserver(e=>{for(let t of e)if(t.type===`childList`)for(let e of t.addedNodes)e.tagName===`LINK`&&e.rel===`modulepreload`&&n(e)}).observe(document,{childList:!0,subtree:!0});function t(e){let t={};return e.integrity&&(t.integrity=e.integrity),e.referrerPolicy&&(t.referrerPolicy=e.referrerPolicy),t.credentials=e.crossOrigin===`use-credentials`?`include`:e.crossOrigin===`anonymous`?`omit`:`same-origin`,t}function n(e){if(e.ep)return;e.ep=!0;let n=t(e);fetch(e.href,n)}})();var e=[{src:`photos/action-dribble.jpg`,alt:`Abdellah Moutal en dribble, maillot vert n°24`},{src:`photos/action-strike.jpg`,alt:`Abdellah Moutal en frappe sur le terrain`},{src:`photos/action-duel.jpg`,alt:`Abdellah Moutal en duel avec un adversaire`},{src:`photos/match-midfield.jpg`,alt:`Abdellah Moutal au milieu de terrain`},{src:`photos/portrait-match.jpg`,alt:`Portrait d’Abdellah Moutal après un match`},{src:`photos/training-pitch.jpg`,alt:`Abdellah Moutal à l’entraînement`},{src:`photos/team-white-pitch.jpg`,alt:`Équipe FC Tevragh Zeina en tenue blanche`},{src:`photos/team-green.jpg`,alt:`Équipe FC Tevragh Zeina en tenue verte`}];document.querySelector(`#app`).innerHTML=`
  <div class="noise" aria-hidden="true"></div>

  <header class="nav">
    <a class="nav__brand" href="#top">Moutal</a>
    <nav class="nav__links" aria-label="Navigation principale">
      <a href="#profil">Profil</a>
      <a href="#parcours">Parcours</a>
      <a href="#galerie">Galerie</a>
    </nav>
  </header>

  <main id="top">
    <section class="hero" aria-label="Présentation">
      <div class="hero__media">
        <img
          class="hero__img"
          src="photos/action-dribble.jpg"
          alt="Abdellah Moutal, maillot vert n°24 FC Tevragh Zeina"
          fetchpriority="high"
        />
        <div class="hero__veil"></div>
      </div>
      <div class="hero__content">
        <p class="hero__given">Abdellah</p>
        <h1 class="hero__brand">Moutal</h1>
        <p class="hero__line">Défenseur central &amp; milieu défensif</p>
        <p class="hero__lede">
          Jeune espoir né en 2007, actuellement en Super D1 avec le FC Tevragh Zeina.
        </p>
        <div class="hero__cta">
          <a class="btn btn--primary" href="#parcours">Voir le parcours</a>
          <a class="btn btn--ghost" href="#galerie">Galerie</a>
        </div>
      </div>
    </section>

    <section id="profil" class="section profil reveal">
      <div class="section__intro">
        <p class="eyebrow">Le joueur</p>
        <h2>Un profil athlétique, axé sur la densification du milieu et de l’axe.</h2>
      </div>
      <div class="profil__grid">
        <figure class="profil__photo">
          <img
            src="photos/portrait-white.jpg"
            alt="Portrait d’Abdellah Moutal en tenue blanche"
          />
        </figure>
        <dl class="stats">
          <div>
            <dt>Postes</dt>
            <dd>Défenseur central · Milieu défensif</dd>
          </div>
          <div>
            <dt>Naissance</dt>
            <dd>2007</dd>
          </div>
          <div>
            <dt>Taille</dt>
            <dd>1 m 81</dd>
          </div>
          <div>
            <dt>Poids</dt>
            <dd>64 kg</dd>
          </div>
          <div>
            <dt>Club actuel</dt>
            <dd>FC Tevragh Zeina</dd>
          </div>
          <div>
            <dt>Championnat</dt>
            <dd>Super D1</dd>
          </div>
        </dl>
      </div>
    </section>

    <section id="parcours" class="section parcours reveal">
      <div class="section__intro">
        <p class="eyebrow">Parcours</p>
        <h2>Des championnats jeunes jusqu’à l’élite mauritanienne.</h2>
      </div>
      <ol class="timeline">
        <li>
          <span class="timeline__step">01</span>
          <div>
            <h3>Championnat U15</h3>
            <p>Premières compétitions structurées, formation défensive.</p>
          </div>
        </li>
        <li>
          <span class="timeline__step">02</span>
          <div>
            <h3>Championnat U17</h3>
            <p>Montée en intensité et lecture du jeu entre les lignes.</p>
          </div>
        </li>
        <li>
          <span class="timeline__step">03</span>
          <div>
            <h3>Championnat U19</h3>
            <p>Responsabilités accrues dans l’axe et au milieu défensif.</p>
          </div>
        </li>
        <li>
          <span class="timeline__step">04</span>
          <div>
            <h3>Super D2</h3>
            <p>Passage au football senior, rythme et duels adultes.</p>
          </div>
        </li>
        <li class="timeline__now">
          <span class="timeline__step">05</span>
          <div>
            <h3>Super D1 — FC Tevragh Zeina</h3>
            <p>Évolue actuellement au plus haut niveau national avec le FC Tevragh Zeina.</p>
          </div>
        </li>
      </ol>
      <figure class="parcours__shot">
        <img
          src="photos/team-superd2.jpg"
          alt="Photo d’équipe Championnat Super D2 2025-2026"
        />
        <figcaption>Championnat Super D2 · étape vers la Super D1</figcaption>
      </figure>
    </section>

    <section id="galerie" class="section galerie reveal">
      <div class="section__intro">
        <p class="eyebrow">Galerie</p>
        <h2>Sur le terrain, avec le FC Tevragh Zeina.</h2>
      </div>
      <div class="gallery">
        ${e.map(e=>`
          <figure class="gallery__item">
            <img src="${e.src}" alt="${e.alt}" loading="lazy" />
          </figure>`).join(``)}
      </div>
    </section>
  </main>

  <footer class="footer">
    <div class="footer__brand">
      <span class="footer__name">Abdellah Moutal</span>
      <span class="footer__meta">Jeune espoir · Super D1 · FC Tevragh Zeina</span>
    </div>
    <p class="footer__copy">© ${new Date().getFullYear()} Abdellah Moutal</p>
  </footer>
`;var t=document.querySelectorAll(`.reveal`),n=new IntersectionObserver(e=>{e.forEach(e=>{e.isIntersecting&&(e.target.classList.add(`is-visible`),n.unobserve(e.target))})},{threshold:.12,rootMargin:`0px 0px -8% 0px`});t.forEach(e=>n.observe(e));var r=document.querySelector(`.hero__img`),i=()=>{if(!r)return;let e=Math.min(window.scrollY,480);r.style.transform=`scale(${1.06-e*8e-5}) translate3d(0, ${e*.12}px, 0)`};window.addEventListener(`scroll`,i,{passive:!0}),i(),document.querySelectorAll(`a[href^="#"]`).forEach(e=>{e.addEventListener(`click`,t=>{let n=e.getAttribute(`href`);if(!n||n===`#`)return;let r=document.querySelector(n);r&&(t.preventDefault(),r.scrollIntoView({behavior:`smooth`,block:`start`}),history.replaceState(null,``,n))})});