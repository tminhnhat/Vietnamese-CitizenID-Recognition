
function CanvasToBase64(canvas)
{
    image_base64 = canvas.toDataURL() + "=="
    image_base64 = image_base64.replace("data:image/jpeg;base64,", "")
    image_base64 = image_base64.replace("data:image/png;base64,", "")

    return image_base64
}

function ResizeCanvas(oldCanvas, width, height)
{
    var newCanvas = document.createElement('canvas');
    var newContext = newCanvas.getContext('2d');

    if(width < oldCanvas.width && height < oldCanvas.height)
    {
        oldCanvas = blur(oldCanvas)
    }
    
    //clone data
    newCanvas.width = width;
    newCanvas.height = height;
    newContext.drawImage(oldCanvas, 0, 0, width, height);  

    return newCanvas
}

function ConvertImageToBase64(img, maxSize)
{
    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    aspect = img.width / img.height

    if(img.width > 1000 || img.height > 1000)
    {               
        if(img.width > img.height)
        {
            canvas.width = 1000;
            canvas.height = canvas.width / aspect;
        }
        else
        {
            canvas.height = 1000;
            canvas.width = canvas.height * aspect;
        }                                
    }
    else
    {
        canvas.width = img.width
        canvas.height = img.height
    }

    ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    return CanvasToBase64(canvas)
}

function blur(c) 
{
    var ctx = c.getContext("2d");
    ctx.globalAlpha = 0.3;

    var offset = 1;


    ctx.drawImage(c, offset, 0, c.width - offset, c.height, 0, 0, c.width-offset, c.height);
    ctx.drawImage(c, 0, offset, c.width, c.height - offset, 0, 0,c.width, c.height-offset);

    return c
};

function LoadUrlToCanvas(canvas, url)
{
    var ctx = canvas.getContext('2d');
    var img = new Image;
    img.onload = function(){
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height); // Or at whatever offset you like
    };
    img.src = url;
}