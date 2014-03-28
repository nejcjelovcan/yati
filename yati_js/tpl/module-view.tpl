<div class="row">
    <div class="small-12 medium-12 columns module-view">
        <ul class="side-nav" data-bind="foreach: modules">
            <li>
                <h5><a data-bind="text: name, attr: { href: '#' + $root.language() + '/' + id() }" /></h5>
                <div class="progress large-6"><span class="meter" data-bind="style { width: progress }"></span></div>
            </li>
        </ul>
    </div>
</div>
