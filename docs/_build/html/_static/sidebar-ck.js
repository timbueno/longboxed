/*
 * sidebar.js
 * ~~~~~~~~~~
 *
 * This script makes the Sphinx sidebar collapsible.
 *
 * .sphinxsidebar contains .sphinxsidebarwrapper.  This script adds
 * in .sphixsidebar, after .sphinxsidebarwrapper, the #sidebarbutton
 * used to collapse and expand the sidebar.
 *
 * When the sidebar is collapsed the .sphinxsidebarwrapper is hidden
 * and the width of the sidebar and the margin-left of the document
 * are decreased. When the sidebar is expanded the opposite happens.
 * This script saves a per-browser/per-session cookie used to
 * remember the position of the sidebar among the pages.
 * Once the browser is closed the cookie is deleted and the position
 * reset to the default (expanded).
 *
 * :copyright: Copyright 2007-2011 by the Sphinx team, see AUTHORS.
 * :license: BSD, see LICENSE for details.
 *
 */$(function(){function f(){return n.is(":not(:visible)")}function l(){f()?h():c()}function c(){n.hide();t.css("width",o);e.css("margin-left",s);v.css({"margin-left":"0",height:e.height()});v.find("span").text("»");v.attr("title",_("Expand sidebar"));document.cookie="sidebar=collapsed"}function h(){e.css("margin-left",r);t.css("width",i);n.show();v.css({"margin-left":i-12,height:e.height()});v.find("span").text("«");v.attr("title",_("Collapse sidebar"));document.cookie="sidebar=expanded"}function p(){n.css({"float":"left","margin-right":"0",width:i-28});t.append('<div id="sidebarbutton"><span>&laquo;</span></div>');var r=$("#sidebarbutton");a=r.css("background-color");var s;window.innerHeight?s=window.innerHeight:s=$(window).height();r.find("span").css({display:"block","margin-top":(s-t.position().top-20)/2});r.click(l);r.attr("title",_("Collapse sidebar"));r.css({color:"#FFFFFF","border-left":"1px solid "+u,"font-size":"1.2em",cursor:"pointer",height:e.height(),"padding-top":"1px","margin-left":i-12});r.hover(function(){$(this).css("background-color",u)},function(){$(this).css("background-color",a)})}function d(){if(!document.cookie)return;var e=document.cookie.split(";");for(var t=0;t<e.length;t++){var n=e[t].split("="),r=n[0];if(r=="sidebar"){var i=n[1];i=="collapsed"&&!f()?c():i=="expanded"&&f()&&h()}}}var e=$(".bodywrapper"),t=$(".sphinxsidebar"),n=$(".sphinxsidebarwrapper");if(!t.length)return;var r=e.css("margin-left"),i=t.width(),s=".8em",o=".8em",u=$(".related").css("background-color"),a=$(".document").css("background-color");p();var v=$("#sidebarbutton");d()});