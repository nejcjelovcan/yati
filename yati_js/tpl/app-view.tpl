<section id="yati-app" kb-inject="yati.views.AppView">
  <nav class="top-bar" data-topbar>
    <ul class="title-area">
      <li class="name">
        <h1><a href="#" data-bind="text: title"></a></h1>
      </li>
      <li class="toggle-topbar menu-icon"><a href="#">Menu</a></li>
    </ul>
    <section class="top-bar-section">
      <!-- Right Nav Section -->
      <ul class="right">
        <li class="has-dropdown">
          <a href="#">Language: <span data-bind="text: languageDisplay"></span></a>
          <ul class="dropdown" data-bind="foreach: languages">
            <li>
              <a data-bind="text: display, attr: {href: '#' + id()}"></a>
            </li>
          </ul>
        </li>
      </ul>
    </section>
  </nav>

  <ul class="breadcrumbs">
    <li><a data-bind="attr: {href: '#' + language()}">Home</a></li>
    <li data-bind="css: {hide: view() == 'index', current: view() == 'project'}"><a data-bind="text: project().name(), attr: {href: '#' + language() + '/' + project().id()}"></a></li>
    <li data-bind="css: {hide: view() == 'index' || view() == 'project', current: view() == 'module'}"><a data-bind="text: module().name(), attr: {href: '#' + language() + '/' + project().id() + '/' + module().id()}"></a></li>
  </ul>

  <section data-bind="css: {hide: view() != 'index'}, template: {name: 'index-view', data: $root}"></section>
  <section data-bind="css: {hide: view() != 'project'}, template: {name: 'project-view', data: $root.project}"></section>
  <section data-bind="css: {hide: view() != 'module'}, template: {name: 'module-view', data: $root.module}"></section>
</section>
