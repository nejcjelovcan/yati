<div class="row">
    <div class="small-12 medium-12 columns project-view">
        <ul class="side-nav" data-bind="foreach: project().modules()">
            <li class="list-progress-item">
                <div class="progress radius small-4 right">
                    <span class="meter" data-bind="style { width: progress() + '%' }, text: progress() + '%'"></span>
                </div>
                <h5>
                    <a data-bind="text: name, attr: { href: yati.router.link('module', $parent.project().id(), $root.language() && $root.language().id(), id()) }" />
                </h5>
            </li>
        </ul>
        <!--div data-bind="foreach: project().modules()">
            <div class="row">
                <h5 class="small-8 medium-8 columns"><a data-bind="text: name, attr: { href: yati.router.link('module', $parent.project().id(), $root.language() && $root.language().id(), id()) }" /></h5>
                <div class="progress small-4 medium-4 columns"><span class="meter" data-bind="style { width: progress() + '%' }, text: progress() + '%'"></span></div>
            </div>
        </div-->
    </div>
</div>
