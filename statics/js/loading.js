/**
 * Created by chenliang on 2020/12/31.
 */
function showLoading(timeout)
{
    timeout = timeout || 5000;
    var overDiv = document.createElement("div");
    var loadingDiv = document.createElement("div");
    var childDiv1 = document.createElement("div");
    var childDiv2 = document.createElement("div");
    var childDiv3 = document.createElement("div");
    overDiv.classList.add('over');
    loadingDiv.classList.add('spinner');
    childDiv1.classList.add('bounce1');
    childDiv2.classList.add('bounce2');
    childDiv3.classList.add('bounce3');
    loadingDiv.appendChild(childDiv1);
    loadingDiv.appendChild(childDiv2);
    loadingDiv.appendChild(childDiv3);
    document.body.appendChild(overDiv);
    document.body.appendChild(loadingDiv);
    setTimeout(function()
    {
        document.body.removeChild(overDiv);
        document.body.removeChild(loadingDiv)
    }, timeout);
}

function showImportings() {
    var overDiv = document.createElement("div");
    var loadingDiv = document.createElement("div");
    // var childDiv1 = document.createElement("div");
    // childDiv1.innerHTML('<progress id="upload_progress" value="0" max="100"></progress>');
    var childDiv1 = document.createElement("progress");
    childDiv1.setAttribute('id', 'upload_progress');
    childDiv1.setAttribute('value', 0);
    childDiv1.setAttribute('max', 100);
    overDiv.classList.add('over');
    loadingDiv.classList.add('spinner');
    loadingDiv.appendChild(childDiv1);
}