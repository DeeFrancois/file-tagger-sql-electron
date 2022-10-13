
eel.expose(js_display_file);
function js_display_file(filename,db){
    console.log(filename);
    var exts = filename.split('.').pop();
    console.log(exts);
    if (exts=='jpg' || exts=='png' || exts=='jpeg' || exts=='jfif'){
        
        document.getElementsByClassName('video-player')[0].style.display='none';
        document.getElementsByClassName('video-player')[0].src='';

        document.getElementsByClassName('img-player')[0].style.display='block';
        document.getElementsByClassName('img-player')[0].src = 'files/'+db+'/'+filename;
    }else{
        document.getElementsByClassName('img-player')[0].style.display='none';
        document.getElementsByClassName('img-player')[0].style.scr='';

        document.getElementsByClassName('video-player')[0].style.display='block';
        document.getElementsByClassName('video-player')[0].src='files/'+db+'/'+filename;
        
}
}

eel.expose(js_display_tags);
function js_display_tags(tags){
    console.log(tags)
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
eel.py_update_index(e);
//instead of doing the script manually here, I can just make a request to change the index
//and then have the python react to that index change in basically the same way as the right control button

}
function clickPress(event){
console.log(event);
if(event.key=="Enter" && event.srcElement.id=="control-bar"){
    var new_db = document.getElementById('control-bar').value;
    eel.py_open_new_db(new_db,document.querySelector('#control-genthumbs').checked,document.querySelector('#control-shuffle').checked);
    document.getElementById('control-bar-label').innerText=document.getElementById('control-bar').value+'.db';
    document.getElementById('control-bar').value='';
    
}
else if(event.key=="Enter" && event.srcElement.id=="input-tags"){
    if (source_mode){
        console.log('Adding source to video');
        eel.py_set_source(document.querySelector('#input-tags').value);
        document.getElementById('input-tags').value='';
        if(!source_hold){
            console.log("Unheld");
        toggle_source();
        }
        
    }
    else if(delete_mode){
        console.log('Deleting tags');
        eel.py_delete_tags_from_video(document.getElementById('input-tags').value);
        document.getElementById('input-tags').focus();
        document.getElementById('input-tags').value='';
        if(!delete_hold){
            console.log("Unheld");
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
// // console.log(event);    
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
$(window).resize(function(e){
    // window.resizeTo(size[0],size[1]);
    console.log(document.body.getBoundingClientRect().width);
    if (document.body.getBoundingClientRect().width > 1700){
        console.log("Img width: ",document.querySelector('.img-container').style.width);
        Array.from(document.querySelectorAll('.img-container')).forEach(e=>e.style.width='10%');
        // size_checkpoint=size_checkpoint*1.3;
    }
    
    else if (document.body.getBoundingClientRect().width > 1000){
        console.log("Img width: ",document.querySelector('.img-container').style.width);
        Array.from(document.querySelectorAll('.img-container')).forEach(e=>e.style.width='12.5%');
        // size_checkpoint=size_checkpoint*1.3;
    }
});

eel.expose(js_add_to_drawer);
function js_add_to_drawer(e,folder_choice){
    console.log("HEREEEE");
$('<div>',{
    class:'img-container'
}).append($('<img>',{
    class:'drawer-image',
    src:`files/thumbs/${folder_choice}/`+e.replace('.webm','.jpg').replace('.mp4','.jpg'),
    'data-img':`files/${folder_choice}/`+e,
    onclick:`swap_video('${e.replace('thumbs/','')}')`
})).append($('<div>',{
    class:'img-overlay',
    text:'Delete',
    onclick:`delete_image(this,'${e}')`
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
console.log("REMOVED TOP ROW");
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
console.log(button.innerText);
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
console.log(elem);
const curr_elem = elem;
var src = curr_elem.src;
console.log(curr_elem.dataset.img);
eel.py_hide_image(curr_elem.dataset.img);
elem.parentNode.remove();
elem.remove();
console.log("Removed");
}
function delete_image(elem,filename){
console.log(elem.parentNode);
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
let opt = document.createElement('option');
opt.value = '+ Create New Database';
document.querySelector('#suggestions').appendChild(opt);
Array.from(the_list).forEach(function(e){
    console.log(e);
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

document.getElementsByClassName('control-box-button')[0].onclick=function(){
    //unfinished
    console.log("database creation routine");
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
    console.log("Manually triggered");
    console.log(e);
    var new_db = document.getElementById('control-bar').value;
    eel.py_open_new_db(new_db,document.querySelector('#control-genthumbs').checked,document.querySelector('#control-shuffle').checked);
    document.getElementById('control-bar-label').innerText=document.getElementById('control-bar').value+'.db';
    document.getElementById('control-bar').value='';
});
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
eel.py_initial_routine();
// eel.py_populate_drawer();
// document.querySelector('.bottomdrawer-container').addEventListener('scroll',function(){
//     console.log("SCROLLED");
// });




});
