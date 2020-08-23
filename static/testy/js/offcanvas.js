$(document).ready(function (event) {
  $(document).on("click", "#like", function (event) {
    event.preventDefault();
    var pk = $(this).attr("value");
    $.ajax({
      type: "POST",
      url: '{% url "like_post" %}',
      data: { id: pk, csrfmiddlewaretoken: "{{ csrf_token }}" },
      dataType: "json",
      success: function (response) {
        $("#like-section").html(response["form"]);
        console.log($("#like-section").html(response["form"]));
      },
      error: function (rs, e) {
        console.log(rs.responseText);
      },
    });
  });
});
