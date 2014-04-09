<section id="yati-app" kb-inject="yati.views.AppView">
  <nav class="top-bar" data-topbar>
    <ul class="title-area">
      <li class="name">
        <h1><a href="#" data-bind="text: title"></a></h1>
      </li>
      <li class="toggle-topbar menu-icon"><a href="#">Menu</a></li>
    </ul>
    <section class="top-bar-section">
      <!--ul class="right">
        <li class="has-dropdown">
          <a href="#">Language: <span data-bind="text: languageDisplay"></span></a>
          <ul class="dropdown" data-bind="foreach: languages">
            <li>
              <a data-bind="text: display, attr: {href: '#' + id()}"></a>
            </li>
          </ul>
        </li>
      </ul-->
    </section>
  </nav>

  <section data-bind="template: {name: 'breadcrumbs-view', data: $root}"></section>
  <section data-bind="css: {hide: !(view() == 'index' || view() == 'project')}, template: {name: 'index-view', data: $root}"></section>
  <section data-bind="css: {hide: view() != 'language'}, template: {name: 'language-view', data: $root}"></section>
  <section data-bind="css: {hide: view() != 'module'}, template: {name: 'module-view', data: $root}"></section>
  <!--section data-bind="css: {hide: view() != 'sourceAdd'}, template: {name: 'source-add-view', data: $root}"></section-->
</section>
