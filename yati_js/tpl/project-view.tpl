<div class="row">
    <div class="small-12 medium-12 columns project-view">
        <h4 data-bind="text: 'Project: ' + name()"></h4><br/>
        <div data-bind="foreach: modules">
            <div class="row">
                <h5 class="small-6 medium-6 columns"><a data-bind="text: name, attr: { href: link() }" /></h5>
                <div class="progress small-6 medium-6 columns"><span class="meter" data-bind="style { width: progress() + '%' }, text: progress() + '%'"></span></div>
            </div>
        </div>
    </div>
</div>
