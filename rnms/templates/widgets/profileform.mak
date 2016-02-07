<form id="${id}" data-parsley-validate class="form-horizontal form-label-left">
    <div class="form-group">
      <label class="control-label col-md-3 col-sm-3 col-xs-12" for="display-name">Username
      </label>
      <div class="col-md-6 col-sm-6 col-xs-12 has-feedback">
        <input type="text" id="display-name" readonly class="form-control has-feedback-left col-md-7 col-cs-12" placeholder="Username">
        <span class="fa fa-user form-control-feedback left" aria-hidden="true"></span>
      </div>
    </div>
    <div class="form-group">
      <label class="control-label col-md-3 col-sm-3 col-xs-12" for="display-name">Display Name <span class="required">*</span>
      </label>
      <div class="col-md-6 col-sm-6 col-xs-12 has-feedback">
        <input type="text" id="display-name" required="required" class="form-control has-feedback-left col-md-7 col-cs-12" placeholder="Display Name">
        <span class="fa fa-user form-control-feedback left" aria-hidden="true"></span>
      </div>
    </div>
    <div class="form-group">
      <label class="control-label col-md-3 col-sm-3 col-xs-12" for="email">Email <span class="required">*</span>
      </label>
      <div class="col-md-6 col-sm-6 col-xs-12 has-feedback">
        <input type="text" id="email" required="required" class="form-control has-feedback-left form-control col-md-7 col-xs-12" placeholder="you@your.isp">
        <span class="fa fa-envelope form-control-feedback left" aria-hidden="true"></span>
      </div>
    </div>
    <div class="ln_solid"></div>
    <div class="form-group">
      <div class="col-md6 col-sm-6 col-xs-12 col-md-offset-3">
        <a href="/"><input type="button" class="btn btn-primary" value="Cancel"></a>
        <button type="submit" class="btn btn-success">Submit</button>
      </div>
    </div>
</form>
