<div class="pagination-centered">
    <ul class="pagination">
        <li data-bind="css: {unavailable: page() == 1}" class="arrow">
            <a data-bind="attr: {href: pageLink(1)}">&laquo;</a>
        </li>
        <li class="unavailable" data-bind="style: {display: page() < 5 ? 'none' : 'inline-block'}">&hellip;</li>
        <!-- ko foreach: pages -->
            <li data-bind="css: {current: $parent.page() == page}">
                <a data-bind="text: page, attr: {href: $parent.pageLink(page)}"></a>
            </li>
        <!-- /ko -->
        <li class="unavailable" data-bind="style: {display: page() > pageCount() - 4 ? 'none' : 'inline-block'}">&hellip;</li>
        <li data-bind="css: {unavailable: page() == pageCount()}" class="arrow">
            <a data-bind="attr: {href: pageLink(pageCount())}">&raquo;</a>
        </li>
    </ul>
</div>
<!--ul class="pagination" data-bind="foreach: pages">
        <li data-bind="css: {current: $parent.page() == page && page == text, unavaliable: unavaliable, arrow: arrow}">
            <a data-bind="html: text, attr: {href: unavaliable ? null : link}"></a>
        </li>
    </ul-->
