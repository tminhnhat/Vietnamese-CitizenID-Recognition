function ExpandRect(rect, scaleRatioX, scaleRatioY)
{
    if (scaleRatioX == 1 && scaleRatioY == 1)
        return rect;
    r = rect;
    r.x -= (r.width * scaleRatioX - r.width) / 2;
    r.y -= (r.height * scaleRatioY - r.height) / 2;
    r.width *= scaleRatioX;
    r.height *= scaleRatioY;

    return r;
}

function IsRectInsideMat(rect, matWidth, matHeight, padding)
{
    
    if(padding == null) padding = 0

    if (rect.x < padding || rect.y < padding)
		return false;
	if (rect.x + rect.width > matWidth - padding)
		return false;
	if (rect.y + rect.height > matHeight - padding)
		return false;
	return true;
}