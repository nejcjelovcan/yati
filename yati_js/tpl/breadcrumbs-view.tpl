<ul class="breadcrumbs">
  <li>
    <a href="#">Home</a>
  </li>
  <li data-bind="css: {hide: view() == 'index', current: view() == 'project'}">
    <a data-bind="text: project().name(), attr: {href: yati.router.link('project', project().id())}"></a>
  </li>
  <li data-bind="css: {hide: view() == 'index' || view() == 'project', current: view() == 'language'}">
    <a data-bind="text: language().display(), attr: {href: yati.router.link('language', project().id(), language().id())}"></a>
  </li>
  <li data-bind="css: {hide: view() != 'module', current: view() == 'module'}">
    <a data-bind="text: module().name(), attr: {href: yati.router.link('module', project().id(), language().id(), module().id())}"></a>
  </li>
</ul>