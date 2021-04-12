import "../scss/main.scss";
import jQuery from "jquery";
const $ = jQuery;

var url = "https://api.bitbucket.org/2.0/repositories/alexlitvin/grail/downloads";
var user_arch = 'x32';
var user_platform = 'Unknown';
var ua = navigator.platform.toLowerCase();

if (/(windows|win95|win32|win64)/.test(ua)){
  user_platform = 'Windows';
} else if (/(linux|freebsd|ssl-mm)/.test(ua)){
  user_platform = 'Linux';
} else if (/(mac os|mac_powerpc)/.test(ua)){
  user_platform = 'Mac';
}

if (user_platform === 'Windows' && /(win64|x64|amd64)/.test(ua) >= 0){
  user_arch = 'x64';
}

var request = new XMLHttpRequest();
request.onreadystatechange = function(){
  if (request.readyState === 4 && request.status === 200)
    (function (response){
      var html = "";
      var text = $('#downloads_table a').text();
      var first = 1;
      var versions = [];

      if (response['values']){
        for (var i=0, l=response['values'].length; i<l;i++){
          var item = response['values'][i];
          var name = item.name;
          var arch = 'x32';
          var platform = 'Windows';

          if (name.indexOf('.dmg') > 0){
            platform = "Mac";
            arch = 'x64';
          }

          if (name.indexOf('64') > 0){
            arch = 'x64';
          }

          var match = arch === user_arch && platform === user_platform && --first === 0;
          var version = name.match(/([0-9.]+[0-9]+)/);

          versions.push([version ? version[0] : '', match, item.links.self.href]);

          html += '<tr>'+
              '<td class="text-left"><b>' + name + '</b></td>' +
              '<td>' + platform + '</td>' +
              '<td>' + arch + '</td>' +
              '<th><a href="' + item.links.self.href + '" class="btn btn-sm '+(match ? 'btn-primary' : 'btn-outline-primary')+'" target="_blank">'+text+'</a></th>' +
            '</tr>';
        }

        $('#downloads_table').append(html);
      }

      versions = versions.sort(function (a, b){
          if (a[1] === b[1]){
            return (a[0] < b[0]) ? -1 : (a[0] > b[0]) ? 1 : 0;
          } else {
            return a[1] < b[1] ? -1 : 1;
          }
        });

      if (versions.length > 0){
        $('#grail_version').text(versions[versions.length-1][0]);
        $('#download_primary').attr('href', versions[versions.length-1][2]);
      }
    })(JSON.parse(request.responseText));
};
request.open("GET", url, true);
request.send(null);

$('#downloads_other').click(function (event){
  event.preventDefault();
  $('#downloads_table').toggleClass('d-none');
});

$(function (){
  var a = $('#cover').outerHeight(true);
  var b = $('#cover main').outerHeight(true);

  $('#cover').height(b > a ? b * 1.15 : null);
});