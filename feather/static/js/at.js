var emojis = [
    "smile", "blush", "relaxed", "sob", "heart_eyes", "kissing_heart", "flushed", "iphone", "girl", "smiley", "heart", "kiss", "copyright", "coffee",
    "a", "ab", "airplane", "alien", "ambulance", "angel", "anger", "angry",
    "arrow_forward", "arrow_left", "arrow_lower_left", "arrow_lower_right",
    "arrow_right", "arrow_up", "arrow_upper_left", "arrow_upper_right",
    "art", "astonished", "atm", "b", "baby", "baby_chick", "baby_symbol",
    "balloon", "bamboo", "bank", "barber", "baseball", "basketball", "bath",
    "bear", "beer", "beers", "beginner", "bell", "bento", "bike", "bikini",
    "bird", "birthday", "black_square", "blue_car", "blue_heart", "blush",
    "boar", "boat", "bomb", "book", "boot", "bouquet", "bow", "bowtie",
    "boy", "bread", "briefcase", "broken_heart", "bug", "bulb",
    "person_with_blond_hair", "phone", "pig", "pill", "pisces", "plus1",
    "point_down", "point_left", "point_right", "point_up", "point_up_2",
    "police_car", "poop", "post_office", "postbox", "pray", "princess",
    "punch", "purple_heart", "question", "rabbit", "racehorse", "radio",
    "up", "us", "v", "vhs", "vibration_mode", "virgo", "vs", "walking",
    "warning", "watermelon", "wave", "wc", "wedding", "whale", "wheelchair",
    "white_square", "wind_chime", "wink", "wink2", "wolf", "woman",
    "womans_hat", "womens", "x", "yellow_heart", "zap", "zzz", "+1",
    "-1", "0", "1", "109", "2", "3", "4", "5", "6", "7", "8", "8ball", "9"
]

var emojis = $.map(emojis, function(value, i) {return {key: value + ':', name:value}});

$(function(){
    $('textarea').atWho(':', {
        data: emojis,
        tpl:"<li data-value='${key}'>${name} <img src='http://a248.e.akamai.net/assets.github.com/images/icons/emoji/${name}.png'  height='20' width='20' /></li>"
    })
    /*.atWho("-",{
        data: icons,
        tpl: "<li data-value='${name}' data-insert='${content}'>${name} ${content}</li>",
        choose: "data-insert"
    });*/

    prettyPrint()
});
