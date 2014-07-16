<div class="row">
    <div class="small-12 columns index-view">
        <dl class="accordion" data-bind="foreach: projects">
            <dd>
                <div class="accordion-head">
                    <ul class="button-group radius right" data-bind="css: {hide: $parent.project().id() != id() || !canChange()}">
                      <!--li><a href="#" class="button tiny secondary"><span class="fa fa-upload" />Upload pofile</a></li-->
                      <li><a data-bind="attr: {href: yati.router.link('project', id())}, css: {hide: $parent.view() == 'project'}" class="button tiny secondary"><!--span class="fa fa-users"/-->List languages</a></li>
                      <li><a data-bind="attr: {href: yati.router.link('project_users', id())}, css: {hide: $parent.view() == 'project_users'}" class="button tiny secondary"><span class="fa fa-users"/>Manage users</a></li>
                      <li><a data-bind="attr: {href: yati.router.link('project_users_add', id())}, css: {hide: $parent.view() == 'project_users_add'}" class="button tiny secondary"><span class="fa fa-plus"/>Add user</a></li>
                    </ul>
                    <a class="" data-bind="text: name(), attr: { href: yati.router.link('project', id()) }"></a>
                </div>
                <div data-bind="css: {hide: $parent.project().id() != id() || $parent.view() != 'project'}">
                    <ul class="side-nav">
                        <!-- ko foreach: targetlanguages -->
                            <li class="list-progress-item">
                                <div class="progress radius small-4 right">
                                    <span class="meter" data-bind="style { width: progress() + '%' }, text: progress() + '%'"></span>
                                </div>
                                <h5>
                                    <a data-bind="attr: {href: yati.router.link('language', $parent.id(), id()) }">
                                        <span data-bind="attr: {class: 'left f32 ' + country()}"></span>
                                        <span data-bind="text: display"></span>
                                    </a>
                                </h5>
                            </li>
                        <!-- /ko -->
                    </ul>
                </div>
                <div data-bind="css: {hide: $parent.project().id() != id() || $parent.view() != 'project_users'}">
                    <table data-bind="foreach: users" style="display: block">
                            <tr>
                                <td>
                                    <span data-bind="text: email()"></span>
                                </td>
                                <td>
                                    <span class="fa fa-check" data-bind="css: {hide: !is_active()}" title="Active"></span>
                                    <span class="fa fa-ban" data-bind="css: {hide: is_active()}" title="Never logged in"></span>
                                </td>
                                <td>
                                    <span data-bind="css: {hide: !is_active() }, text: moment(last_login()).fromNow()"></span>
                                    <span data-bind="css: {hide: is_active()}">Never logged in</span>
                                </td>
                                <td>
                                    <!-- ko foreach: languages -->
                                        <span data-bind="attr: {class: 'right f32 ' + country(), title: display()}"/>
                                    <!-- /ko -->
                                </td>
                                <td class="small-6">
                                    <input type="text" disabled="disabled" data-bind="css: {hide: is_active()}, attr: {value: yati.router.link_invite(invite_token())}"/>
                                </td>
                            </tr>
                    </table>
                    <a href="#" class="button tiny secondary" data-bind=" attr: { href: yati.router.link('project_users_add', $parent.project().id()) }"><span class="fa fa-plus"> Add user</a>
                </div>
                <div data-bind="template: {name: 'user-add', data: $parent.project()}, css: {hide: $parent.project().id() != id() || $parent.view() != 'project_users_add'}">
                </div>
            </dd>
        </dl>
    </div>
</div>
