public class StrongNightVoter implements AccessDecisionVoter {
    @Override
    public int vote(Authentication authentication, Object object, Collection collection) {

      Calendar calendar = Calendar.getInstance();
      int currentHour = calendar.get(Calendar.HOUR_OF_DAY);
      if(currentHour >= 8 && currentHour <= 19) {
        return ACCESS_GRANTED;
      }
      // users are not allowed to connect during the night
      return ACCESS_DENIED;
    }
}