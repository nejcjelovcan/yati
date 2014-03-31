<div class="row">
    <div class="small-12 medium-12 columns module-view">
        <h4 data-bind="text: $root.project().name() + ': ' + name()"></h4>
        <div class="units-container" data-bind="foreach: units()">
            <div class="row units-row">
                <div class="small-6 medium-6 columns units-left" data-bind="text: msgid0">
                </div>
                <div class="small-6 medium-6 columns units-left" data-bind="text: msgstr0">
                </div>
            </div>
        </div>
    </div>
</div>
