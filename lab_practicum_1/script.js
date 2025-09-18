let length = (x1, x2, y1, y2) => {
    return Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
}
document.getElementById("CalculateButton").addEventListener('click', () =>
{


    let x1 = document.getElementById("x1").value ;
    let x2 = document.getElementById("x2").value ;
    let y1 = document.getElementById("y1").value ;
    let y2 = document.getElementById("y2").value ;

    let result = length(x1, x2, y1, y2);

    if (document.getElementById("result"))document.getElementById("result").remove();
    let p = document.createElement('p');
    p.setAttribute('id' , "result");
    p.innerHTML = "Результат = " + `${result}`;
    document.querySelector('.loan-forms').appendChild(p);
}
);