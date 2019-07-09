/**
 * Created by Daniel on 13.04.2016.
 */


// Selectors
var logoDivSelector, logoImgSelector, containerSelector, selectedLogoInGallery = null
var logo_width_form_selector, logo_id_form_selector,logo_left_pos_form_selector,logo_top_pos_form_selector,container_reduction_ratio_form_selector = null

// Variables about image modification to send to the back-end
var ParametersToSend = {
    logo_id: null,
    logo_width: null,
    logo_left_pos: null,
    logo_top_pos: null,
    container_reduction_ratio: null
};


$(function () {
    initializeSelectors();
    setupBaseImageAndDraggableLogo();
    $("#saveButton").click(saveButtonActivation); // Make the image and go to a new window
    $("#gallery .image").click(manageLogoSwitch); // Manage the switch of the logo selection
    selectLogoInGallery($("#first-image"));
});


function setupBaseImageAndDraggableLogo() {
    //Global parameters to set
    var MAX_RATIO_IMAGE_SIZE_IN_WINDOWS_HEIGHT = 0.6,
        MAX_RATIO_IMAGE_SIZE_IN_WINDOWS_WIDTH = 0.5,
        LOGO_MIN_WIDTH_RATIO = 0.05,
        LOGO_MIN_HEIGHT_RATIO = 0.05,
        LOGO_INITIAL_WIDTH_RATIO = 0.3,
        LOGO_INITIAL_HEIGHT_RATIO = 0.3;


    // Calculate the image ratio for the container
    var maxH = $(window).height() * MAX_RATIO_IMAGE_SIZE_IN_WINDOWS_HEIGHT,
        maxW = $(window).width() * MAX_RATIO_IMAGE_SIZE_IN_WINDOWS_WIDTH;
    var ratioToDivideBy = Math.max(base_image_height / maxH, base_image_width / maxW);

    var newImageHeight = base_image_height / ratioToDivideBy,
        newImageWidth = base_image_width / ratioToDivideBy;

    // Setup the div and background size for the base image
    containerSelector.css({"height": newImageHeight});
    containerSelector.css({"width": newImageWidth});
    containerSelector.css({"background-size": newImageWidth + "px " + newImageHeight + "px"});


    //Setup the logo size and options (draggable, resizable)
    var logoMinWidth = newImageWidth * LOGO_MIN_WIDTH_RATIO,
        logoMinHeight = newImageHeight * LOGO_MIN_HEIGHT_RATIO,
        logoInitialWidth = newImageWidth * LOGO_INITIAL_WIDTH_RATIO;

    logoDivSelector.css({"width": logoInitialWidth});

    logoDivSelector.draggable({
        containment: "#container"
    });

    logoDivSelector.resizable({
        aspectRatio: true,
        containment: "#container",
        minHeight: logoMinHeight,
        minWidth: logoMinWidth,
    });

    ParametersToSend.container_reduction_ratio = ratioToDivideBy;
}


//Manage the behavior of the save button. Gather the data it needs and then make the link.
function saveButtonActivation() {
    var logoPosition = logoImgSelector.offset();
    var containerPosition = containerSelector.offset();

    ParametersToSend.logo_left_pos = logoPosition.left - containerPosition.left;
    ParametersToSend.logo_top_pos = logoPosition.top - containerPosition.top;
    ParametersToSend.logo_width = logoImgSelector.css("width");

    //displayParametersInformation();

    // Attributing to the form all the image properties
    logoWidthWithoutPx = String(ParametersToSend.logo_width).replace("px", "");
    leftPosFloat = String(ParametersToSend.logo_left_pos);
    topPosFloat = String(ParametersToSend.logo_top_pos);

    logo_width_form_selector.attr("value", logoWidthWithoutPx);
    logo_id_form_selector.attr("value", ParametersToSend.logo_id);
    logo_left_pos_form_selector.attr("value", leftPosFloat);
    logo_top_pos_form_selector.attr("value", topPosFloat);
    container_reduction_ratio_form_selector.attr("value", ParametersToSend.container_reduction_ratio);
}


// Manage the switch of the logo selection
function manageLogoSwitch(event) {
    if (selectedLogoInGallery != null) {
        selectedLogoInGallery.removeClass("selectedBorder");
        selectedLogoInGallery.addClass("normalBorder");
    }
    // Firstly we want the link to the logo image, and secondly to change the "src" of the main logo image.
    // The user clicks either on the "img" or "description" tag. The parent is the "a" tag (link).
    // The "img" child of "a" is the logo. We then take the source and put it instead of the current one.
    var a_tag = $(event.target).parent();
    var img_tag = a_tag.children('img');
    var newsrc = img_tag.attr('src');
    logoImgSelector.attr("src", newsrc);
    selectLogoInGallery(a_tag.parent())
}



// Initialize the selectors with the right id's from the HTML code
function selectLogoInGallery(selector) {
    // We want to change the parent "div" (which has class "image"). The parent of "a" is precisely this "div".
    // We will change the global variables to send. We will also change the border (switch class).
    selectedLogoInGallery = selector;
    ParametersToSend.logo_id = selectedLogoInGallery.attr("data-id");
    selectedLogoInGallery.addClass("selectedBorder");
    selectedLogoInGallery.removeClass("normalBorder");


    //Change the size of the div of the parent.
    logoDivSelector.css({"width": logoImgSelector.css("width")});
    logoDivSelector.css({"height": logoImgSelector.css("height")});
}


// Initialize the selectors with the right id's from the HTML code
function initializeSelectors() {
    logoDivSelector = $("#logoID");
    logoImgSelector = $("#imgLogoID");
    containerSelector = $("#container");
    logo_id_form_selector = $(logo_id_form_selector_text)
    logo_width_form_selector = $(logo_width_form_selector_text)
    logo_left_pos_form_selector = $(logo_left_pos_form_selector_text)
    logo_top_pos_form_selector = $(logo_top_pos_form_selector_text)
    container_reduction_ratio_form_selector = $(container_reduction_ratio_form_selector_text)
}

//Display the parameters information. Useful for debugging.
function displayParametersInformation() {
    var infoString = "Selected logo id = "
        + ParametersToSend.logo_id + "   ; Logo width = " + ParametersToSend.logo_width +
        " ; Logo left/top position = " + ParametersToSend.logo_left_pos + " / " + ParametersToSend.logo_top_pos +
        "  ; Ratio to divide = " + ParametersToSend.container_reduction_ratio;
    $("#tempInfo").text(infoString);
}
