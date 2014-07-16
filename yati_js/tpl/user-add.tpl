<form data-bind="submit: invite_user().onSubmit">
    <div class="row">
        <div class="large-12 columns">
            <h5>Enter e-mail to add a new user.</h5>
            <p>Invite link will be generated that will ask the user to set password which will activate the account.</p>
        </div>
        <div class="large-12 columns" data-bind="css: {error: invite_user().emailError}">
            <label>E-mail
                <input type="text" name="email" placeholder="" data-bind="value: invite_user().email, valueUpdate: 'input'"/>
            </label>
            <small class="error" data-bind="css: {hide: !invite_user().emailError()}, text: invite_user().emailError"></small>
        </div>
    </div>
    <div class="row">
        <div class="large-6 medium-12 columns">
            <label>Language
                <div data-bind="template: {name: 'language-selector', data: invite_user()}"></div>
            </label>
        </div>
        <div class="small-12 columns">
            <a href="#" class="right button small" data-bind="click: invite_user().onSubmit, css: {disabled: invite_user().submitting()}">Add user</a>
        </div>
    </div>
</form>