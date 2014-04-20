<section id="yati-app" kb-inject="yati.views.AppView">
  <section data-bind="template: {name: 'breadcrumbs-view', data: $root}"></section>
  
  <section data-bind="css: {hide: !(view() == 'index' || view() == 'project')}, template: {name: 'index-view', data: $root}"></section>
  <section data-bind="css: {hide: view() != 'language'}, template: {name: 'language-view', data: $root}"></section>
  <section data-bind="css: {hide: view() != 'module'}, template: {name: 'module-view', data: $root}"></section>
  <section class="terms" data-bind="css: {hide: !terms().length}, template: {name: 'terms-view', data: $root}"></section>
  <!--section data-bind="css: {hide: view() != 'sourceAdd'}, template: {name: 'source-add-view', data: $root}"></section-->
</section>
