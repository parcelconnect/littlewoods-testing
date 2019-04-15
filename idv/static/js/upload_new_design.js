"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};
const MaxFileSize = 4194304;  // 4 MBs

function readFileAsBinaryString(file) {
  return new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => {
      resolve(fr.result);
    };
    fr.readAsBinaryString(file);
  });
}

function logError(message, extra) {
  if (typeof Raven !== 'undefined') {
    Raven.captureMessage(message, {
      extra: extra
    });
  } else {
    console.log(message);
    console.log(extra);
  }
}

function chainFuncs(funcs) {
  return funcs.reduce((promiseChain, currentTask) =>
      promiseChain.then(chainResults =>
        currentTask().then(currentResult => {
          chainResults.push(currentResult);
          return chainResults;
        })
      )
    , Promise.resolve([]));
}

function uploadFile(file, signed_url, content_md5, progressBars) {
  return new Promise((resolve, reject) => {
    $.ajax({
      url: signed_url,
      type: "PUT",
      data: file,
      dataType: "text",
      contentType: file.type,
      headers: {'Content-MD5': content_md5},
      processData: false,
      xhr: function () {
        const xhr = new window.XMLHttpRequest();
        progressBars.update(xhr, file);
        return xhr;
      }
    }).done(function () {
      resolve();
    }).fail(function (jqXHR, textStatus, error) {
      const message = 'Error uploading file';
      logError(message, {
        status: jqXHR.status,
        response: jqXHR.response,
        textStatus: textStatus,
        error: error
      });
      reject(message);
    });
  });
}

class FieldErrors {
  constructor(errors) {
    this.errors = errors;
  }
}

class IDVForm {
  constructor(email, account_number, csrfmiddlewaretoken, files, successCb, failCb, date_1, date_2) {
    this.email = email;
    this.account_number = account_number;
    this.csrfmiddlewaretoken = csrfmiddlewaretoken;
    this.file_data = {};
    this.md5_calculation = [];
    this.successCallback = successCb;
    this.failCallback = failCb;
    this.date_1 = date_1;
    this.date_2 = date_2;

    const create_lambda_assign_file_md5 = (filename) => {
      return (md5) => {this.file_data[filename]['content_md5'] = md5;}
    };

    for(const file of files) {
      this.file_data[file.name] = {
        'content_type': file.type,
        'file': file
      };
      this.md5_calculation.push(
        readFileAsBinaryString(file).then(function (binaryString) {
          const md5 = CryptoJS.MD5(CryptoJS.enc.Latin1.parse(binaryString));
          const base64 = CryptoJS.enc.Base64.stringify(md5);
          return base64;
        }).then(create_lambda_assign_file_md5(file.name)).catch((err) => console.log(err))
      );
    }

    this.md5_calculation = Promise.all(this.md5_calculation);
  }

  _sign_s3_put_url(filename) {
    const formData = new FormData();
    formData.append('email', this.email);
    formData.append('account_number', this.account_number);
    formData.append('csrfmiddlewaretoken', this.csrfmiddlewaretoken);
    formData.append('files_info', JSON.stringify({
      [filename]: this.file_data[filename]}));
    formData.append('date_1', this.date_1);
    formData.append('date_2', this.date_2);
    return fetch(Django.Data.get('sign_s3_request_url'), {
        method: "POST",
        credentials: "same-origin",
        body: formData
    }).then((response) => {
      if (response.status === 200) {
        return response.json().then((files) => {
          for (const filename in files) {
            this.file_data[filename]['signed_url'] = files[filename];
          }
        });
      }
      if (response.status === 400) {
        throw FieldErrors(response.json()['errors']);
      }

      const error_msg = 'Unexpected response when submitting id verification form: status ' + response.status;
      logError(error_msg, {status: response.status, response: response.body});
      throw error_msg;
    })
  }

  _upload_files(progressBars) {
    let signed_urls = [];
    for (const filename in this.file_data) {
      signed_urls.push(() => this._sign_s3_put_url(filename)
        .then(() => {
          const data = this.file_data[filename];
          return {upload: uploadFile(data.file, data.signed_url, data.content_md5, progressBars)}
        }))
    }
    return chainFuncs(signed_urls);
  }

  cancel() {
    this.successCallback = () => {};
    this.failCallback = (error) => {};
  }

  send(progressBars) {
    return this.md5_calculation
      .then(() => this._upload_files(progressBars))
      .then((upload_files) => Promise.all(upload_files.map((res => res.upload))))
      .then(() => this.successCallback())
      .catch((error) => this.failCallback(error));
  }
}

IDV.FormUtils = (function() {
  var my = {};
  var errorClass = 'has-error';
  var errorListClass = 'error-list';

  var createErrorList = function(errors) {
    var $errorList = $('<ul class="' + errorListClass + '"></ul>');

    for (const error of errors) {
      $errorList.append('<li>' + error + '</li>');
    };
    return $errorList;
  }

  my.fieldHasError = function(element) {
    $(element).closest('.form-group').hasClass(errorClass);
  }

  my.addFieldErrors = function(element, errors) {
    $(element).closest('.form-group').addClass(errorClass);
    var $errorList = createErrorList(errors);
    $(element).after($errorList);
  }

  my.clearFieldErrors = function(element) {
    $(element).closest('.form-group').removeClass(errorClass);
    $(element).siblings('.' + errorListClass).remove();
  }

  my.clearErrors = function() {
    $('.form-group').removeClass(errorClass);
    $('.'+errorListClass).remove();
  }

  my.focusOnFirstErrorInput = function() {
    var firstErrorContainer = $('.form-group.' + errorClass)[0];
    var firstErrorInput = $(firstErrorContainer).find('input')[0];
    $(firstErrorInput).focus();
  }

  return my;
})();

/*
 * Adds and updates upload progress bars.
 */
IDV.ProgressBars = (function() {
  const my = {};
  const containerID = 'progress-bars';
  const progressBarTemplateContainerID = 'progress-bar-template-container';
  let $container = null;

  my.reset = function() {
    $container.html('');
  };

  function add(file) {
    const $templateContainer = $('#'+progressBarTemplateContainerID).clone();
    $templateContainer.find('.filename').html(file.name);
    $templateContainer.find('.progress-bar').attr('data-filename', file.name)
    const $bar = $templateContainer.children();
    $container.append($bar);
  };

  my.addMany = function(files) {
    for (const file of files) {
      add(file);
    };
  };

  my.update = function(xhr, file) {
    xhr.upload.addEventListener("progress", function(evt) {
      if (evt.lengthComputable) {
        let percentComplete = evt.loaded / evt.total;
        percentComplete = Math.floor(percentComplete * 100);
        $container.find('[data-filename="'+file.name+'"]')
          .css('width', percentComplete+'%')
          .attr('aria-valuenow', percentComplete);
        if (percentComplete === 100) {
          $('.progress-bar').addClass('progress-bar-success');
        }
      }
    }, false);
  };

  my.init = function() {
    $container = $('#'+containerID);
  };

  return my;
})();

IDV.UploadForm = (function() {
  const imageMimeTypes = ["image/*"];
  const docMimeTypes = [
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.oasis.opendocument.text",
    "text/plain"
  ];

  const my = {};
  const formID = 'id-docs';
  let $form = null;
  let progressBars = null;
  let fileInputsCount = 1;
  let currentIDVForm = null;

  function isImageType(mimeType) {
    return mimeType.match(imageMimeTypes.join("|"))
  }

  function isDocumentType(mimeType) {
    return mimeType.match(docMimeTypes.join("|"))
  }

  function createImageThumbnail(picFile, name) {
    return `<img class='thumbnail' src='${picFile.result}' title='${name}'/>`;
  }

  function createDocUploadInfo() {
    return `<div class='thumbnail-container'>Document uploaded</div>`;
  }

  function drawThumbnailForSection(file, input_id) {
    const thumbnail_placeholder = $("#" + input_id + "-thumbnail");
    thumbnail_placeholder.empty();
    if (isImageType(file.type)) {
      const picReader = new FileReader();
      const div = document.createElement("div");
      thumbnail_placeholder.append(div);
      $(picReader).on("load", function(event) {
          div.innerHTML = createImageThumbnail(event.target, file.name);
      });
      picReader.readAsDataURL(file);
    }
    else {
      const div = createDocUploadInfo();
      thumbnail_placeholder.append(div);
    }
  }

  function processSelectedFiles(event) {
    const file = typeof event.target.files[0] !== "undefined" ? event.target.files[0] : null
    const filename = file ? event.target.files[0].name : null;
    if (file && !isDocumentType(file.type) && !isImageType(file.type)) {
      event.target.value = "";
      displayModal('files-invalid-template');
      return;
    }

    if (file.size > MaxFileSize) {
      event.target.value = "";
      displayModal('files-size-invalid-template');
      return;
    }

    if (!!file) {
      drawThumbnailForSection(file, event.target.id);
    }

    const output = $("#files-upload-result");
    output.empty();

    const filesInput = $('input[type="file"]');
    const files = [];
    for (const fileHandler of filesInput) {
      if (fileHandler.files.length) {
        if (!files.includes(fileHandler.files[0])) {
          files.push(fileHandler.files[0]);
        }
      }
    }

    if(files.length > 0) {
      $(".file-input-checker").hide()
    } else {
      $(".file-input-checker").show()
    }

    const imgCount = files.filter(file => isImageType(file.type)).length;
    const docCount = files.filter(file => isDocumentType(file.type)).length;
    const infoText = document.createElement("p");
    infoText.innerText = `${imgCount} image(s) selected, ${docCount} document(s) selected`;
    output.prepend(infoText)
  }

  function warnIfNotSupportingThumbnails() {
    if(!window.File || !window.FileList || !window.FileReader) {
      const output = $("#files-upload-result");
      const warning = document.createElement("p");
      warning.innerText = "Sorry, your browser does not support image thumbnails";
      output.append(warning);
      return;
    }

    $form.on('change', 'input[type="file"]', function(event) {
      processSelectedFiles(event);
    });
  }

  function showUploadSuccessMessage() {
    const content = $('#successful-upload-template').html();
    const imagePreview = $("#files-upload-result").clone();
    imagePreview.find('p').remove();
    $('#content-wrapper').html(content).append(imagePreview)
  }

  function displayModal(divId) {
    $('#js-modal .modal-content').html($('#' + divId).html());
    $('#js-modal').modal('show');
    // To be able to continue filling form without the need to refresh page.
    $form.find("[type=submit]").prop("disabled", false);
  }

  function failedSignHandler(error) {
    if (error instanceof FieldErrors) {
      const errors = error.errors;
      for (const fieldName in errors) {
        const $field = $('input[name="' + fieldName + '"]');
        const fieldErrors = errors[fieldName];
        IDV.FormUtils.addFieldErrors($field, fieldErrors);
      }
      IDV.FormUtils.focusOnFirstErrorInput();
      return;
    }

    displayModal('failed-upload-template');
  }

  function getFormFiles() {
    const $fileInput = $form.find('input[type="file"]');
    let files = [];
    for (const fileHandler of $fileInput) {
      if (typeof fileHandler.files[0] !== 'undefined') {
        files.push(fileHandler.files[0]);
      }
    }
    return files;
  }

  function submitHandler(event) {
    $form.find("[type=submit]").prop("disabled", true);
    event.preventDefault();

    if (currentIDVForm !== null) {
      currentIDVForm.cancel();
    }

    function dateIsInFuture(date) {
      let provided_date = new Date(date);
      let now = new Date();
      return provided_date > now;
    }

    const upload_sections_amount = $form.find("[type=file]").length
    const files = getFormFiles();
    if (files.length < upload_sections_amount) {
      displayModal('files-required-template');
      return;
    }
    progressBars.reset();
    progressBars.addMany(files);

    const date_1 = $('#files-address-proof-1-issue-date').val();
    const date_2 = $('#files-address-proof-2-issue-date').val();

    if (!date_1 | !date_2) {
      displayModal('dates-required-template');
      return;
    }

    for(const date of [date_1, date_2]) {
      if (dateIsInFuture(date)) {
        displayModal('dates-not-in-future-template');
        return;
      }
    }

    const email = $('#lwi-email-address').val();
    const account_number = $('#lwi-account-number').val();
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    currentIDVForm = new IDVForm(email, account_number, csrf, files,
      showUploadSuccessMessage, failedSignHandler, date_1, date_2);
    IDV.FormUtils.clearErrors();

    currentIDVForm.send(progressBars).then(() => {
      $form.find("[type=submit]").prop("disabled", false);
    })
  }

  function checkUploadSupport() {
    return !($('#files-1').disabled || navigator.userAgent.match(/(Android (1.0|1.1|1.5|1.6|2.0|2.1))|(Windows Phone (OS 7|8.0))|(XBLWP)|(ZuneWP)|(w(eb)?OSBrowser)|(webOS)|(Kindle\/(1.0|2.0|2.5|3.0))/));
  }

  my.init = function() {
    progressBars = IDV.ProgressBars;
    progressBars.init();

    $form = $('#' + formID);
    $form.submit(submitHandler);

    if (typeof MobileDetect !== 'undefined') {
      const md = new MobileDetect(window.navigator.userAgent);
      if (!md.mobile()) {
        $("input[type=file]").attr("accept", imageMimeTypes.concat(docMimeTypes).join(", "));
      }
    }

    if (!checkUploadSupport()) {
      displayModal('upload-unsupported-template');
    } else  {
      //pass
    }

    warnIfNotSupportingThumbnails();
  };
  return my;
})();

$(function() {
  IDV.UploadForm.init();

  const $requiredFields = $(':input[required=""],:input[required]');
  $requiredFields.keydown(function() {
    IDV.FormUtils.clearFieldErrors(this);
  });
});
