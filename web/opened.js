
var timer_running = 1;
var loop_video_flag = 0;
var pinned =0;
var loop_flag=0;
var autoplay_next_video_flag=0;
var idle_skip_flag =0;
var mute_flag=0;
var sidebar_flag=1;
var drawer_flag=1;
var time;
var inactivityTime = function () {
    window.onload = resetTimer;
    // DOM Events
    document.onmousemove = resetTimer;
    document.onkeydown = resetTimerLonger;
    // repeater();
    time=setInterval(eel.py_right_control, 2000);
    function resetTimer() {
        if(idle_skip_flag){
        clearTimeout(time);
        time=setInterval(eel.py_right_control, 2000);
        }
        // 1000 milliseconds = 1 second
    }
    function resetTimerLonger() {
        if(idle_skip_flag){
        clearTimeout(time);
        time=setInterval(eel.py_right_control, 6000);
        }
        // 1000 milliseconds = 1 second
    }
};
// toggle_loop">Loop</button>
//             <button class="middle-button" onclick="toggle_autoplay">Autoplay</button>
//             <button class="middle-button" onclick="toggle_mute">Mute</button>
//             <button class="middle-button" onclick="toggle_sidebar">Hide Sidebar</button>
//             <button class="middle-button" onclick="toggle_drawer
function toggle_idle_skip(){
    // console.log("TOGGLE IDLE SKIP", idle_skip_flag);
    if(idle_skip_flag==1){
        clearTimeout(time);
        idle_skip_flag=0;
    }
    else{
        idle_skip_flag=1;
    }
}
function toggle_autoplay_next(){
    if(autoplay_next_video_flag){
        autoplay_next_video_flag=0;
    }
    else{
        autoplay_next_video_flag=1;
    }
}
function toggle_mute(){
    if(mute_flag){
        mute_flag=0;
        document.querySelector('.video-player').muted=false;
    }
    else{
        mute_flag=1;
        document.querySelector('.video-player').muted=true;
    }
}
function toggle_sidebar(){
    if(sidebar_flag){
        sidebar_flag=0;
        hide_sidebar();
    }
    else{
        sidebar_flag=1;
        show_sidebar();
    }
}
function toggle_drawer(){
    if(drawer_flag){
        drawer_flag=0;
        hide_drawer();
    }
    else{
        drawer_flag=1;
        show_drawer();
    }
    
}
function toggle_loop(){
    if(loop_flag){
        loop_flag=0;
        document.querySelector('.video-player').loop=false;
    }
    else{
        loop_flag=1;
        document.querySelector('.video-player').loop=true;
    }
    
}
function hide_sidebar(){
    document.querySelector('.sidebar-container').style.display='none';
    document.querySelector('.video-container').style.width='100%';

    document.querySelector('.control-box').style.display='none';
    document.querySelector('.drawer-image-container').style.width='100%';
}
function show_sidebar(){
    document.querySelector('.sidebar-container').style.display='inline-block';
    document.querySelector('.video-container').style.width='70%';

    document.querySelector('.control-box').style.display='inline-block';
    document.querySelector('.drawer-image-container').style.width='70%';
}
function hide_drawer(){
    document.querySelector('.drawer-image-container').style.display='none';
    document.querySelector('.control-box').style.display='none';
    document.querySelector('.top-container').style.height='95%';
    document.querySelector('.top-container').style.maxHeight='95%';
    // document.querySelector('.top-container').style.paddingBottom='20px';
    // document.querySelector('.middle-button-container').className+=' footermode';
    // height: 68vh;
    // max-height: 68vh;
}
function show_drawer(){
    document.querySelector('.drawer-image-container').style.display='inline-block';
    document.querySelector('.control-box').style.display='inline-block';
    document.querySelector('.top-container').style.height='68vh';
    document.querySelector('.top-container').style.maxHeight='68vh';
    document.querySelector('.middle-button-container').className='middle-button-container';
}

eel.expose(js_confirmation)
function js_confirmation(db_name){
    if(confirm(db_name + '.db does not exist. Create New Database? ')){
        // console.log("Creating");
        eel.py_open_new_db(db_name,1,document.querySelector('#control-shuffle').checked);

    }else{
        // console.log("Nevermind");
    }
}

eel.expose(js_display_file);
function js_display_file(filepath,db){
    // console.log(filepath);
    var exts = filepath.split('.').pop();
    // console.log(exts);
    if (exts=='jpg' || exts=='png' || exts=='jpeg' || exts=='jfif'){
        
        document.getElementsByClassName('video-player')[0].style.display='none';
        document.getElementsByClassName('video-player')[0].src='';

        document.getElementsByClassName('img-player')[0].style.display='block';
        document.getElementsByClassName('img-player')[0].src = 'atom://'+filepath;
    }else{
        document.getElementsByClassName('img-player')[0].style.display='none';
        document.getElementsByClassName('img-player')[0].style.scr='';

        document.getElementsByClassName('video-player')[0].style.display='block';
        document.getElementsByClassName('video-player')[0].src='atom://'+filepath;
        
}
}

eel.expose(js_display_tags);
function js_display_tags(tags){
    // console.log(tags)
    try{
    document.getElementsByClassName('current-tags')[0].innerText=tags.join(' ');
    }
    catch(e){
        document.getElementsByClassName('current-tags')[0].innerText=tags;
    }
}

eel.expose(js_display_source);
function js_display_source(filename,source){
    // console.log(shortened_source);
    document.querySelector('.source-bar').innerText=`- Filename: ${filename} | Source: ${source}`;
}
function swap_video(e){
    // console.log("SWAPVIDEO:");
    // console.log(e);
eel.py_update_index(e);
//instead of doing the script manually here, I can just make a request to change the index
//and then have the python react to that index change in basically the same way as the right control button

}
function clickPress(event){
// console.log(event);
if(event.key=="Enter" && event.srcElement.id=="control-bar"){
    var new_db = document.getElementById('control-bar').value;
    eel.py_check_if_exists(new_db,document.querySelector('#control-genthumbs').checked,document.querySelector('#control-shuffle').checked);
    document.getElementById('control-bar-label').innerText=document.getElementById('control-bar').value+'.db';
    document.getElementById('control-bar').value='';
    
}
else if(event.key=="Enter" && event.srcElement.id=="input-tags"){
    if (source_mode){
        // console.log('Adding source to video');
        eel.py_set_source(document.querySelector('#input-tags').value);
        document.getElementById('input-tags').value='';
        if(!source_hold){
            // console.log("Unheld");
        toggle_source();
        }
        
    }
    else if(delete_mode){
        // console.log('Deleting tags');
        eel.py_delete_tags_from_video(document.getElementById('input-tags').value);
        document.getElementById('input-tags').focus();
        document.getElementById('input-tags').value='';
        if(!delete_hold){
            // console.log("Unheld");
            toggle_delete();
        }
    }

    else{
    eel.py_set_tags(document.getElementById('input-tags').value);
    document.getElementById('input-tags').value='';
    }

}
}

function scrollerfunc(event){
// if (event.deltaY<0){
// return;
// }
// console.log(event);    
// const scrollMax = document.querySelector('.bottomdrawer-container').scrollHeight - document.querySelector('.bottomdrawer-container').clientHeight
// const scrollval = document.querySelector('.bottomdrawer-container').scrollTop;
// console.log(scrollMax-scrollval);
// if (scrollMax-scrollval<170){
//     eel.py_request_more_filenames();
// }
}
var size = [909,690];
var source_mode = 0;
var delete_mode = 0;
var delete_hold = 0;
var source_hold = 0;
function adjust_thumb_widths(){
    let curr_width = (document.body.getBoundingClientRect().width/909 * 100 - 100).toFixed(0);
    // console.log(curr_width+'%');
    if ( curr_width%20 ==0){
        // console.log("RESIZE");
        document.querySelectorAll('.img-container').forEach(e=>e.style.width=100/(5+(curr_width/20))+'%');

    }
}
$(window).resize(function(e){

    // window.resizeTo(size[0],size[1]);
    // console.log(document.body.getBoundingClientRect().width);
    adjust_thumb_widths();
    if(document.body.getBoundingClientRect().width<540){
        if(sidebar_flag=1){
        hide_sidebar();
        sidebar_flag=0;
        }
    }
    // else{
    //     show_sidebar();
    //     sidebar_flag=1;
    // }
    // if (document.body.getBoundingClientRect().width > 1700){
        // console.log("Img width: ",document.querySelector('.img-container').style.width);
    //     Array.from(document.querySelectorAll('.img-container')).forEach(e=>e.style.width=100/15+'%');
    //     // size_checkpoint=size_checkpoint*1.3;
    // }
    
    // else if (document.body.getBoundingClientRect().width > 1100){
        // console.log("Img width: ",document.querySelector('.img-container').style.width);
    //     Array.from(document.querySelectorAll('.img-container')).forEach(e=>e.style.width=100/9+'%');
    //     // size_checkpoint=size_checkpoint*1.3;
    // }
    // else if (document.body.getBoundingClientRect().width > 500){
        // console.log("Img width: ",document.querySelector('.img-container').style.width);
    //     Array.from(document.querySelectorAll('.img-container')).forEach(e=>e.style.width=100/5+'%');
    //     // size_checkpoint=size_checkpoint*1.3;
    // }
});

eel.expose(js_add_to_drawer);
function js_add_to_drawer(e,folder_choice,thumb_path){
    // console.log(e);
    // console.log("HEREEEE");
$('<div>',{
    class:'img-container'
}).append($('<img>',{
    class:'drawer-image',
    src:`${thumb_path}`,
    'data-img':e,
    click:function(){swap_video(e)}
})).append($('<div>',{
    class:'img-overlay',
    text:'Delete',
    click:function(){delete_image(this,e)}
})).appendTo('.drawer-image-container');

}

eel.expose(js_add_to_tagfield);
function js_add_to_tagfield(e){
$('<button>',{
    class:'tag-button',
    text:e,
    onclick:`get_batch_based_on(this)`
}).appendTo('.sidebar-container');
}

eel.expose(js_clear_drawer);
function js_clear_drawer(){
document.querySelectorAll('.img-container').forEach(e=>e.remove());
}
eel.expose(js_clear_taglist);
function js_clear_taglist(){
document.querySelectorAll('.tag-button').forEach(e=>e.remove());
}
eel.expose(js_remove_top_row); //Unfinished
function js_remove_top_row(){
// console.log("REMOVED TOP ROW");
Array.from(document.querySelectorAll('.drawer-image')).slice(0,5).forEach(e=>e.remove());
}
eel.expose(js_change_database_label);
function js_change_database_label(db){
document.querySelector('#control-bar-label').innerText=db;
}

function js_open_video(filename){
document.getElementsByClassName('video-player').src=filename;

}

function get_batch_based_on(elem){
const button = elem;
// console.log(button.innerText);
eel.py_retrieve_batch_with_tag(button.innerText);
if (button.classList.contains('clicked')){
    // button.className=button.className.replace('clicked ','');
    Array.from(document.querySelectorAll('.clicked')).forEach(e=>e.className='tag-button');
}
else{
    if(document.querySelectorAll('.clicked').length>0){
        Array.from(document.querySelectorAll('.clicked')).forEach(e=>e.className='tag-button');
    }
    button.className='clicked tag-button';
}
// eel.py_retrieve_batch(button)
}
function hide_image(elem){
// console.log(elem);
const curr_elem = elem;
var src = curr_elem.src;
// console.log(curr_elem.dataset.img);
eel.py_hide_image(curr_elem.dataset.img);
elem.parentNode.remove();
elem.remove();
// console.log("Removed");
}
function delete_image(elem,filename){
// console.log(elem.parentNode);
elem.parentNode.remove();
eel.py_delete_image(filename,document.querySelector('#control-delete').checked);
// elem.parentNode.remove();
// elem.remove();
}

function toggle_delete(){
document.getElementById('input-tags').focus();
if (document.querySelector('.delete-button').classList.contains('p-clicked')){ 
    document.querySelector('.delete-button').className='delete-button'; //deselect
    delete_mode= 0;

}
else{ //select
    document.querySelector('.delete-button').className='p-clicked delete-button';
    delete_mode = 1;
}
document.getElementById('input-tags').focus();
}

function toggle_source(){
if (document.querySelector('.source-button').classList.contains('p-clicked')){ 
    document.querySelector('.source-button').className='source-button'; //deselect
    source_mode= 0;
    

}
else{ //select
    document.querySelector('.source-button').className='p-clicked source-button';
    source_mode = 1;
}
document.getElementById('input-tags').focus();
}
eel.expose(js_trigger_hover);
function js_trigger_hover(){ //Works but a bit buggy
document.querySelector('.video-player').onmouseover();
setTimeout(function(){
    document.querySelector('.video-player').onmouseleave();
},500);
document.querySelector('.img-player').onmouseover();
setTimeout(function(){
    document.querySelector('.img-player').onmouseleave();
},500);
}

eel.expose(js_update_autocomplete);
function js_update_autocomplete(the_list){
document.querySelectorAll('option').forEach(e=>e.remove());
Array.from(the_list).forEach(function(e){
    // console.log(e);
    let opt = document.createElement('option');
    opt.value=e.split('.db')[0];
    document.querySelector('#suggestions').appendChild(opt);

})

}

$(document).ready(function(){
document.body.onmousedown = function(e) {
    if(e.button == 1) {
        e.preventDefault();
        return false;
    }
}

$(document).bind("keydown", function(e){ 
    if (e.target.nodeName.toLowerCase()=='input'){
        if (!e.target.value==''){
            return;
        }
    }
    e = e || window.event;
    var charCode = e.which || e.keyCode;
    if(charCode == 39) eel.py_right_control();
    if(charCode == 37) eel.py_left_control();
});
$('.drawer-image-container').mousedown(function(e){
    if (e.which=== 3){
        var src = e.target.src;
        // console.log(src.split('/').pop());
        hide_image(e.target);
        // console.log(e.target.src());
    }
    else if(e.which === 2){
        var src = e.target.src;
        // console.log(src.split('/').pop());
        // console.log(src.split('/').pop());
        eel.py_open_file(e.target.dataset.img);
    }
});


document.getElementById('input-tags').focus();
document.getElementById('input-tags').value='';

document.getElementsByClassName('right-button')[0].onclick=function(){

    eel.py_right_control();
    eel.py_get_tags();

    document.getElementById('input-tags').focus();
    document.getElementById('input-tags').value='';

}

document.getElementsByClassName('left-button')[0].onclick=function(){
    eel.py_left_control();
    eel.py_get_tags();

    document.getElementById('input-tags').focus();
    document.getElementById('input-tags').value='';
}

// document.getElementsByClassName('delete-button')[0].onclick=function(){
//     toggle_delete();
// }
$('.delete-button').mousedown(function(event){
    if(event.which==1){
        delete_hold=0;
    }
    else if (event.which==3){
        delete_hold=1;
    }
    toggle_delete();
});

$('.source-button').mousedown(function(event){
    if(event.which==1){
        source_hold=0;
    }
    else if (event.which==3){
        source_hold=1;
    }
    toggle_source();
});

// document.getElementsByClassName('source-button')[0].onclick=function(){
//     toggle_source();
    
// }
document.querySelector('.control-bar').addEventListener('change',function(e){
    // console.log("Manually triggered");
    // console.log(e);
    var new_db = document.getElementById('control-bar').value;
    eel.py_check_if_exists(new_db,document.querySelector('#control-genthumbs').checked,document.querySelector('#control-shuffle').checked);
    document.getElementById('control-bar-label').innerText=document.getElementById('control-bar').value+'.db';
    document.getElementById('control-bar').value='';
});
document.querySelector('.top-pin').addEventListener('click',function(e){
    // console.log("Pinning");
    if(pinned==0){
    pinned=1;
    e.target.innerText='◈';
    }
    else{
        pinned=0;
        e.target.innerText='◇';
    }

});
document.querySelector('.video-player').onended=function(){
    // console.log("Video ended");
    // What you want to do after the event
    if (autoplay_next_video_flag==1){
        eel.py_right_control();
    }
};

document.querySelector('.video-player').onmouseover=function(){
    document.querySelector('.source-bar').className='source-bar';
}
document.querySelector('.video-player').onmouseleave=function(){
    document.querySelector('.source-bar').className='hidden source-bar';
}

document.querySelector('.img-player').onmouseover=function(){
    document.querySelector('.source-bar').className='source-bar';
}
document.querySelector('.img-player').onmouseleave=function(){
    document.querySelector('.source-bar').className='hidden source-bar';
}
inactivityTime();
eel.py_initial_routine();
// eel.py_populate_drawer();
// document.querySelector('.bottomdrawer-container').addEventListener('scroll',function(){
    // console.log("SCROLLED");
// });




});
