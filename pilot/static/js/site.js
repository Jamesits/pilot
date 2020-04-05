function flow_self_delete() {
    fetch('flow/self', {
        method: 'DELETE',
    }).catch(function () {
        alert("request failed");
    }).finally(function () {
        window.location.reload();
    });
}

function flow_self_apply(rule_id) {
    rule_id = parseInt(rule_id);

    fetch('flow/self', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `rule=${rule_id}`,
    }).catch(function () {
        alert("request failed");
    }).finally(function () {
        window.location.reload();
    });
}
