"use strict";

var IDV = window.IDV || {};
var Django = window.Django || {};

(function(a){(jQuery.browser=jQuery.browser||{}).mobile=/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4))})(navigator.userAgent||navigator.vendor||window.opera);

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
      const message = 'Error uploading Photo ID file';
      logError(message, {status: jqXHR.status, response: jqXHR.response});
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
  constructor(email, account_number, csrfmiddlewaretoken, files) {
    this.email = email;
    this.account_number = account_number;
    this.csrfmiddlewaretoken = csrfmiddlewaretoken;
    this.file_data = {};
    this.md5_calculation = [];

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

  _sign_s3_put_url() {
    const formData = new FormData();
    formData.append('email', this.email);
    formData.append('account_number', this.account_number);
    formData.append('csrfmiddlewaretoken', this.csrfmiddlewaretoken);
    formData.append('files_info', JSON.stringify(this.file_data));
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
    const uploads = [];
    for (const filename in this.file_data) {
      const data = this.file_data[filename];
      uploads.push(uploadFile(data.file, data.signed_url, data.content_md5, progressBars))
    }
    return Promise.all(uploads);
  }

  send(progressBars) {
    return this.md5_calculation
      .then(() => this._sign_s3_put_url())
      .then(() => this._upload_files(progressBars));
  }
}

IDV.FormUtils = (function() {
  var my = {};
  var errorClass = 'has-error';
  var errorListClass = 'error-list';

  var createErrorList = function(errors) {
    var $errorList = $('<ul class="' + errorListClass + '"></ul>');
    $.each(errors, function(idx, error) {
      $errorList.append('<li>' + error + '</li>');
    });
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
    $.each(files, function(idx, file) {
      add(file);
    });
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
  const my = {};
  const formID = 'id-docs';
  let $form = null;
  let progressBars = null;
  let useMultiple = true;
  let fileInputs = 1;

  function createImageThumbnail(picFile, name) {
    const div = document.createElement("div");
    div.innerHTML = "<img class='thumbnail' src='" + picFile.result + "' " + "title='" + name + "'/>";
    return div;
  }

  function initImageThumbnails() {
    const filesInput = $('input[type="file"]');
    const output = $("#files-upload-result");

    if(!window.File || !window.FileList || !window.FileReader) {
      const warning = document.createElement("p");
      warning.innerText = "Sorry, your browser does not support image thumbnails"
      output.append(warning);
      return;
    }

    filesInput.unbind('change');

    filesInput.on("change", function(event) {
      output.empty();
      let imgCount = 0;

      if (useMultiple) {
        imgCount = appendThumbnail(event.target.files, output);
      } else {
        $('label[for=' + $(this).attr('id') + ']').find('span').html(event.target.files[0].name);
        let files = [];
        $.each(filesInput, function(index, value) {
          if (value.files.length) {
            if (!files.includes(value.files[0])) {
              files.push(value.files[0]);
            }
          }
        });
        imgCount += appendThumbnail(files, output);
      }

      const infoText = document.createElement("p");
      infoText.innerText = imgCount + (imgCount > 1 ? " images" : " image" ) + " selected"

      output.prepend(infoText)
    });
  }

  function appendThumbnail(files, output) {
    let imgCount = 0
    for(let i = 0; i < files.length; i++) {
      const file = files[i];
      if(!file.type.match("image"))
          continue;

      imgCount++;
      const picReader = new FileReader();
      $(picReader).on("load", function(event) {
          const div = createImageThumbnail(event.target, file.name)
          output.append(div);
      });
      picReader.readAsDataURL(file);
    }
    return imgCount;
  }

  function showUploadSuccessMessage() {
    const content = $('#successful-upload-template').html();
    const imagePreview = $("#files-upload-result").clone();
    imagePreview.find('p').remove();
    $('#content-wrapper').html(content).append(imagePreview)
  }

  function uploadFileFailHandler() {
    const content = $('#failed-upload-template').html();
    $('#js-modal .modal-content').html(content);
    $('#js-modal').modal('show');
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

    uploadFileFailHandler();
  }

  function getFormFiles() {
    const $fileInput = $form.find('input[type="file"]');
    if (useMultiple) {
      return $fileInput[0].files;
    }
    let files = [];
    $.each($fileInput, function(index, value){
      files.push(value.files[0]);
    })
    return files;
  }

  function submitHandler(event) {
    event.preventDefault();

    const files = getFormFiles();
    progressBars.reset();
    progressBars.addMany(files);

    const email = $('#lwi-email-address').val();
    const account_number = $('#lwi-account-number').val();
    const csrf = $('input[name="csrfmiddlewaretoken"]').val();
    const idv_form = new IDVForm(email, account_number, csrf, files);
    IDV.FormUtils.clearErrors();

    idv_form.send(progressBars).then(showUploadSuccessMessage).catch(failedSignHandler);
  }

  function showUploadNotSupportedMessage() {
    let content = '<div class="row" style="margin: 2vh auto 2vh auto"><div class="col-md-12">\
        We are currently upgrading our system, please bear with us while we carry out this work, \
        apologies for any inconvenience caused. Please email us at \
        <a href="mailto:validation@shopdirect.com">validation@shopdirect.com</a></div><div>';
    $('#js-modal .modal-content').html(content);
    $('#js-modal').modal('show');
  }

  function checkUploadSupport() {
    if ($('#files').disabled || navigator.userAgent.match(/(Android (1.0|1.1|1.5|1.6|2.0|2.1))|(Windows Phone (OS 7|8.0))|(XBLWP)|(ZuneWP)|(w(eb)?OSBrowser)|(webOS)|(Kindle\/(1.0|2.0|2.5|3.0))/)) {
      return false;
    }
    if (jQuery.browser.mobile) {
      return 'partial';
    }
    const input = document.createElement('input');
    input.setAttribute('multiple', 'true');
    if (input.multiple === true) {
      return true;
    }
    return 'partial';
  }

  function setAlternativeUploadMethod() {
    // Change multiple input behaviour
    useMultiple = false;
    const label = $('.btn-file-upload');
    const new_label = label.clone();
    label.attr('for', 'files-1');
    const input = $('#files');
    input.removeAttr('multiple');
    input.attr('id', 'files-1');
    const button = document.createElement("input");
    button.type = 'button';
    button.value = 'Add more files';
    button.onclick = function() {
      fileInputs++;
      new_label.attr('for', 'files-' + fileInputs);
      const fileInput = document.createElement("input");
      fileInput.type = 'file';
      fileInput.name = 'files';
      fileInput.id = 'files-' + fileInputs;
      fileInput.setAttribute('required', 'required');
      $('input[type=file]:last').after(fileInput).after(new_label.clone()).after('<br/>');
      initImageThumbnails();
    }
    input.after(button).after('<br/>');
  }

  my.init = function() {
    progressBars = IDV.ProgressBars;
    progressBars.init();

    $form = $('#'+formID);
    $form.submit(submitHandler)

    const uploadSupport = checkUploadSupport();
    if (!uploadSupport) {
      showUploadNotSupportedMessage();
    } else if (uploadSupport === 'partial') {
      setAlternativeUploadMethod();
    }

    initImageThumbnails();
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
