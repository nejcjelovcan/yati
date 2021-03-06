<nav class="top-bar" data-topbar>
  <ul class="title-area">
    <li class="name">
      <h1><a href="/">Viidea Localize</a></h1>
    </li>
    <li class="toggle-topbar menu-icon"><a href="#">Menu</a></li>
  </ul>
  <section class="top-bar-section">
    <ul class="right">
      {% if not user.is_anonymous %}
        <li class="has-dropdown">
          <a href="/">{{ user.email }}</a>
          <ul class="dropdown">
            <li><a href="/logout/" class="link-raw">Logout</a></li>
          </ul>
        </li>
        <li class="divider"></li>
      {% endif %}
    </ul>
  </section>
</nav>
