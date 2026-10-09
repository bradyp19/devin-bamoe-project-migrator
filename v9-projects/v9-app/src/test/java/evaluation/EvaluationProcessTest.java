package evaluation;

import io.quarkus.test.junit.QuarkusTest;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.assertNotNull;

@QuarkusTest
public class EvaluationProcessTest {

    @Test
    public void testCompleteEvaluationProcessLifecycle() {
        // 1. Start process instance
        Map<String, Object> payload = Map.of(
            "employee", "john",
            "reason", "Annual performance review",
            "initiator", "admin"
        );

        String processInstanceId = given()
            .contentType(ContentType.JSON)
            .accept(ContentType.JSON)
            .body(payload)
            .when()
            .post("/evaluation")
            .then()
            .statusCode(201)
            .body("id", notNullValue())
            .body("employee", equalTo("john"))
            .body("reason", equalTo("Annual performance review"))
            .extract()
            .path("id");

        assertNotNull(processInstanceId);

        // 2. Fetch Self Evaluation task for user 'john'
        List<Map<String, Object>> tasks = given()
            .accept(ContentType.JSON)
            .when()
            .get("/evaluation/" + processInstanceId + "/tasks?user=john")
            .then()
            .statusCode(200)
            .body("size()", greaterThanOrEqualTo(1))
            .extract()
            .as(List.class);

        String selfEvalTaskId = (String) tasks.get(0).get("id");
        assertNotNull(selfEvalTaskId);

        // 3. Complete Self Evaluation task (providing performance score 4)
        Map<String, Object> selfEvalOutput = Map.of(
            "performance", 4
        );

        given()
            .contentType(ContentType.JSON)
            .accept(ContentType.JSON)
            .body(selfEvalOutput)
            .when()
            .post("/evaluation/" + processInstanceId + "/PerformanceEvaluation/" + selfEvalTaskId + "?user=john")
            .then()
            .statusCode(200);

        // 4. Verify parallel PM and HR Evaluation tasks are created
        List<Map<String, Object>> pmTasks = given()
            .accept(ContentType.JSON)
            .when()
            .get("/evaluation/" + processInstanceId + "/tasks?group=PM")
            .then()
            .statusCode(200)
            .body("size()", greaterThanOrEqualTo(1))
            .extract()
            .as(List.class);

        String pmTaskId = (String) pmTasks.get(0).get("id");

        List<Map<String, Object>> hrTasks = given()
            .accept(ContentType.JSON)
            .when()
            .get("/evaluation/" + processInstanceId + "/tasks?group=HR")
            .then()
            .statusCode(200)
            .body("size()", greaterThanOrEqualTo(1))
            .extract()
            .as(List.class);

        String hrTaskId = (String) hrTasks.get(0).get("id");

        // 5. Complete PM Evaluation task
        given()
            .contentType(ContentType.JSON)
            .accept(ContentType.JSON)
            .body(Map.of())
            .when()
            .post("/evaluation/" + processInstanceId + "/PerformanceEvaluation/" + pmTaskId + "?user=pmUser&group=PM")
            .then()
            .statusCode(200);

        // 6. Complete HR Evaluation task
        given()
            .contentType(ContentType.JSON)
            .accept(ContentType.JSON)
            .body(Map.of())
            .when()
            .post("/evaluation/" + processInstanceId + "/PerformanceEvaluation/" + hrTaskId + "?user=hrUser&group=HR")
            .then()
            .statusCode(200);

        // 7. Verify process instance completed and no longer active
        given()
            .accept(ContentType.JSON)
            .when()
            .get("/evaluation/" + processInstanceId)
            .then()
            .statusCode(404);
    }
}
