jQuery(document).ready(function ($) {
    let cl_gender, cl_age, cl_height_1, cl_weight_1, cl_height_2, cl_height_22, cl_weight_2, cl_activity,
        cl_goal, protein_in = false, fat_in = false, carb_in = false, txt_msg = "";
    let cl_protein, cl_fat, cl_carb;
    let rs_vl, cl_unit = 1;

    const nft = Intl.NumberFormat("en-US", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    });

    $(".cl-slider-in").on("input", function (e) {
        var min = Number(e.target.min),
            max = Number(e.target.max),
            vl = Number(e.target.value),
            val = Number(e.target.value);
            
        let in_id = $(this).attr("id");

        if (min == 0) {
            min = min + 1;
            max = max + 1;
            val = val + 1;
        }

        let bg_size = ((val - min) * 100) / (max - min);

        $(e.target).css({
            backgroundSize: bg_size + "% 100%",
        });

        $("#"+in_id+"_vl").val(vl+"%");

        calc();
    }).trigger("input");

    $("#cl_goal").on("input", function () {
        let vl = Number($(this).val());

        let value = 100;
        let min = 0;
        let max = 100;

        if(vl == 2){
            value = 90;
        } else if(vl == 3) {
            value = 110;
            min = 100;
            max = 150;
        }

        $("#cl_percent").attr("min", min);
        $("#cl_percent").attr("max", max);
        $("#cl_percent").val(value).trigger("input");
        
        calc();
    });

    $(".gen_check").on("click", function () {
        cl_gender = $(this).data("value");
        $(".gen_check").removeClass("active");
        $(this).addClass("active");

        calc();
    });

    $("#cl_activity, .cl-required").on("input", function () {
        calc();
    });

    $(".unit_check").on("click", function () {
        cl_unit = Number($(this).data("value"));
        $(".unit_check").removeClass("active");
        $(this).addClass("active");
        if (cl_unit == 1) {
            $("#metric_inp").css({ "display": "flex" });
            $("#imperial_inp").hide();
        } else {
            $("#metric_inp").hide();
            $("#imperial_inp").css({ "display": "flex" });
        }

        calc();
    });

    $("#cl_email").on("input", function(){
        $("#err_msg").hide();
    })

    $("#btn_send").on("click", function () {
        let in_email = $("#cl_email").val();
        
        if(validateEmailAdd(in_email)){
            $("#err_msg").hide();
            console.log(txt_msg);
            
            $("#fr_email_id").val(in_email);
            $("#fr_msg_id").val(txt_msg);
            $("#fr_sub_btn_id").click();
        } else {
            $("#err_msg").slideDown();
        }
    });

    function calc() {
        cl_age = Number($("#cl_age").val());

        if (cl_unit == 1) {
            cl_height = Number($("#cl_height_1").val());
            cl_weight = Number($("#cl_weight_1").val());
        } else {
            cl_height = ((Number($("#cl_height_2").val()) * 12) + Number($("#cl_height_22").val())) * 2.55;
            cl_weight = Number($("#cl_weight_2").val()) * 0.453592;
        }

        cl_activity = $("#cl_activity").val();
        cl_goal = Number($("#cl_goal").val());

        if (cl_gender && cl_age && cl_height && cl_weight && cl_activity && cl_goal) {
            
            let arr = $("#cl_activity").val().split(",");

            cl_activity = Number(arr[0]);
            cl_protien = Number(arr[1]);


            cl_percent = Number($("#cl_percent").val())/100;
            
            if (cl_gender == "Male") {
                rs_1 = 10 * cl_weight + 6.25 * cl_height - 5 * (cl_age) + 5;
                rs_1 = (rs_1 * cl_activity) * cl_percent;
                cl_fat = 1 * cl_weight;
                rs_5 = cl_fat;
                rs_4 = rs_5 * 9;
            } else {
                rs_1 = 10 * cl_weight + 6.25 * cl_height - 5 * (cl_age) - 161;
                rs_1 = (rs_1 * cl_activity) * cl_percent;
                cl_fat = rs_1 * (40/100);
                rs_4 = cl_fat;
                rs_5 = rs_4 / 9;
            }
            
            rs_3 = cl_protien * cl_weight;
            rs_2 = rs_3 * 4;


            rs_6 = rs_1 - rs_2 - rs_4;
            rs_7 = rs_6/4;

            prcnt_1 = (100/rs_1) * rs_2;
            prcnt_2 = (100/rs_1) * rs_4;
            prcnt_3 = (100/rs_1) * rs_6;

            $('#rs_1').text(nft.format(rs_1));
            $('#rs_2').text(nft.format(rs_2));
            $('#rs_3').text(nft.format(rs_3));
            $('#rs_4').text(nft.format(rs_4));
            $('#rs_5').text(nft.format(rs_5));
            $('#rs_6').text(nft.format(rs_6));
            $('#rs_7').text(nft.format(rs_7));

            $('#prcnt_1').text(nft.format(prcnt_1)+"%");
            $('#prcnt_2').text(nft.format(prcnt_2)+"%");
            $('#prcnt_3').text(nft.format(prcnt_3)+"%");

            txt_msg = `
            Geslacht: ${$(".gen_check.active").text().trim()}
            Leeftijd: ${$("#cl_age").val()}
            Lengte: ${cl_height} cm
            Gewicht: ${cl_weight} lbs
            Activiteitsniveau: ${$("#cl_activity option:selected").text()}
            Doel: ${$("#cl_goal option:selected").text()}

            Eiwitten (${nft.format(prcnt_1)}%):
            -> Calories/day = ${nft.format(rs_2)} (${nft.format(rs_3)} grams)

            Vetten(${nft.format(prcnt_2)}%): 
            -> Calories/day = ${nft.format(rs_4)} (${nft.format(rs_5)} grams)

            Koolhydraten(${nft.format(prcnt_3)}%): 
            -> Calories/day = ${nft.format(rs_6)} (${nft.format(rs_7)} grams)
            `;
        } else {
            $('#rs_1').text(nft.format(0));
            $('#rs_2').text(nft.format(0));
            $('#rs_3').text(nft.format(0));
            $('#rs_4').text(nft.format(0));
            $('#rs_5').text(nft.format(0));
            $('#rs_6').text(nft.format(0));
            $('#rs_7').text(nft.format(0));

            $('#prcnt_1').text(nft.format(0)+"%");
            $('#prcnt_2').text(nft.format(0)+"%");
            $('#prcnt_3').text(nft.format(0)+"%");
        }
    }

    // Validate email input field
    function validateEmailAdd(email) {
        const re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(email);
    }
});